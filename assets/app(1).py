from flask import Flask, request, jsonify, Response
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider
import os
from SalesPDF.generate_sales_plan_pdf import generate_sales_plan_pdf
# import Codes.timetable as tb
from datetime import datetime
import json  # Add this line
from collections import defaultdict  # Add this line if not already present
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

@app.route('/hl')
def index():
    return "ok"

# @app.route("/api/v1/schedule",methods=['POST','GET'])
# def timetable_new():
#     data = request.get_json()
#     if data is None:
#         return '', 400

#     pdf = tb.create_doc_new(data)
#     if not os.path.exists(pdf):
#         return '',500

#     def generate():
#         with open(pdf, "rb") as f:
#             while True:
#                 chunk = f.read()
#                 if not chunk:
#                     break
#                 yield chunk
#     return Response(generate(), content_type="application/octet-stream")

@app.route("/api/v1/timetable",methods=['POST','GET'])
def timetable():
    data = request.get_json()
    if data is None:
        return '', 400

    pdf = tb.create_doc(data)
    if not os.path.exists(pdf):
        return '',500

    def generate():
        with open(pdf, "rb") as f:
            while True:
                chunk = f.read()
                if not chunk:
                    break
                yield chunk
    return Response(generate(), content_type="application/octet-stream")


"""
根据传入参数，下载对应的文件
"""
@app.route("/api/v1/down_pdf", methods=['POST'])
def down_pdf():
    requests_param = request.get_json()
    if requests_param is None:
        return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400

    logging.info(f"Received parameters: {requests_param}")

    stu_name = requests_param['studentName']
    stu_exam_ticket_num = requests_param['examCertNo']
    stu_exam_paper_num = requests_param['examPaperNo']
    stu_exam_result = requests_param['examResult']
    exam_sort = requests_param['examSort']
    cup_year = requests_param['cup_year']
    cup_round = requests_param['cup_round']
    exam_answer_content = requests_param.get('examAnswerContent', '')

    subject, level = stu_exam_paper_num.split('_')
    logging.info(f"Subject: {subject}, Level: {level}")

    # Load JSON data
    try:
        with open(f'data/{cup_year}/{cup_round}/questions_{cup_round}_2025.json') as file:
            all_questions = json.load(file)
        logging.info(f"Successfully loaded JSON data. Total questions: {len(all_questions)}")
    except FileNotFoundError:
        logging.error(f"JSON file not found: data/{cup_year}/{cup_round}/questions_{cup_round}_2025.json")
        return jsonify({'status': 'error', 'message': 'Question data not found'}), 404
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from file")
        return jsonify({'status': 'error', 'message': 'Error reading question data'}), 500

    # Filter questions for this exam
    exam_questions = [q for q in all_questions if q['Subject'] == subject and 
                      q['Level'] == level and
                      q['Year'] == cup_year and q['Round'] == cup_round]
    logging.info(f"Filtered questions for exam. Total exam questions: {len(exam_questions)}")

    # Initialize summary
    summary = {
        'student_name': stu_name,
        'student_id': stu_exam_ticket_num,
        'ans_list': stu_exam_result,
        'xueke': stu_exam_paper_num,
        'cup_round': cup_round
    }

    # Calculate number of topics
    topics = set(q['Topic'] for q in exam_questions)
    summary['num_of_topics'] = len(topics)
    logging.info(f"Number of unique topics: {summary['num_of_topics']}")

    # Process exam results
    topic_results = defaultdict(lambda: {'correct': 0, 'total': 0, 'subtopics': defaultdict(list)})
    
    for q, result, sort_order in zip(exam_questions, stu_exam_result, exam_sort):
        logging.info(f"Processing question: Topic: {q['Topic']}, Result: {result}, Sort Order: {sort_order}")
        topic = q['Topic']
        subtopic = q['Subtopic']
        is_correct = result == '2'
        
        topic_results[topic]['total'] += 1
        if is_correct:
            topic_results[topic]['correct'] += 1
        
        subtopic_index = (sort_order - 1) // 3
        topic_results[topic]['subtopics'][subtopic_index].append((q, is_correct))

    logging.info(f"Processed exam results. Number of topics: {len(topic_results)}")

    # Generate summary entries
    subtopic_keys = []
    for i, (topic, data) in enumerate(topic_results.items(), 1):
        accuracy = round(data['correct'] / data['total'] * 100)
        summary[f'topic{i}'] = topic
        summary[f'topic{i}_accuracy'] = accuracy
        logging.info(f"Topic {i}: {topic}, Accuracy: {accuracy}%")

        for j, (subtopic_index, questions) in enumerate(data['subtopics'].items(), 1):
            subtopic_key = f'topic{i}_{j}'
            subtopic_keys.append(subtopic_key)
            
            # Use topic name if all subtopics are None or empty
            subtopic_names = set(q['Subtopic'] for q, _ in questions if q['Subtopic'])
            if not subtopic_names:
                summary[subtopic_key] = topic
            else:
                summary[subtopic_key] = ' / '.join(subtopic_names)
            
            logging.info(f"Subtopic {subtopic_key}: {summary[subtopic_key]}")

            comments = []
            mistakes = []

            for question, is_correct in questions:
                if is_correct:
                    comment = question['Comment_Correct']
                else:
                    comment = question['Comment_Wrong']
                    mistakes.append(f"Q{question['Question Number']}")
                
                if comment and not comment.endswith('；') and not comment.endswith('。'):
                    comment += '；'
                if comment:
                    comments.append(comment)

            combined_comment = ''.join(comments).rstrip('；') + '。' if comments else ""
            # Apply the replacements
            combined_comment = combined_comment.replace("学生", summary['student_name'] + "同学").replace("XXX", summary['student_name']).replace("。。","。")
            summary[f'{subtopic_key}_comment'] = combined_comment

            mistakes_comment = '错题：' + ', '.join(mistakes) if mistakes else '错题：无'
            # Apply the replacements to mistakes comment as well
            mistakes_comment = mistakes_comment.replace("学生", summary['student_name'] + "同学").replace("XXX", summary['student_name']).replace("。。","。")
            summary[f'{subtopic_key}_comment_mistakes'] = mistakes_comment
            
            # Log the generated comment for each subtopic
            logging.info(f"Subtopic {subtopic_key} comment: {summary[f'{subtopic_key}_comment'][:100]}...")  # Log first 100 characters
            logging.info(f"Subtopic {subtopic_key} mistakes: {summary[f'{subtopic_key}_comment_mistakes']}")

    # Define section1_keys and section2_keys
    total_subtopics = len(subtopic_keys)
    mid_point = (len(topic_results) + 1) // 2  # This ensures a fair split for odd numbers of topics
    summary['section1_keys'] = subtopic_keys[:mid_point]
    summary['section2_keys'] = subtopic_keys[mid_point:]

    # Calculate section1_mark and section2_mark
    section1_correct = sum(topic_results[topic]['correct'] for topic in list(topic_results.keys())[:mid_point])
    section1_total = sum(topic_results[topic]['total'] for topic in list(topic_results.keys())[:mid_point])
    summary['section1_mark'] = round(section1_correct / section1_total * 100, 2) if section1_total > 0 else 0

    section2_correct = sum(topic_results[topic]['correct'] for topic in list(topic_results.keys())[mid_point:])
    section2_total = sum(topic_results[topic]['total'] for topic in list(topic_results.keys())[mid_point:])
    summary['section2_mark'] = round(section2_correct / section2_total * 100, 2) if section2_total > 0 else 0

    logging.info(f"Section 1 Mark: {summary['section1_mark']}%")
    logging.info(f"Section 2 Mark: {summary['section2_mark']}%")

    logging.info(f"Generated summary. Number of subtopics: {total_subtopics}")
    logging.info(f"Summary keys: {summary.keys()}")
    logging.info(f"Topic accuracies: {[summary.get(f'topic{i}_accuracy') for i in range(1, summary['num_of_topics'] + 1)]}")
    logging.info(f"Topics: {list(topic_results.keys())}")
    logging.info(f"Section 1 topics: {list(topic_results.keys())[:mid_point]}")
    logging.info(f"Section 2 topics: {list(topic_results.keys())[mid_point:]}")

    # At the end of the down_pdf function, before returning
    comment_count = sum(1 for key in summary.keys() if key.endswith('_comment'))
    logging.info(f"Total number of comment fields generated: {comment_count}")

    pdf_path = generate_pdf(summary)

    # print(student_info)
    #student_info = {'stu_name': '张三', 'stu_exam_ticket_num': 'VC20210001', 'stu_exam_paper_num': 'maths_lv1', 'stu_exam_result': '021022211021120120120120120120120'}
    now = datetime.now()
    time_string = now.strftime("%Y%m%d%H%M%S") + str(now.microsecond // 1000).zfill(3)
    oss_file_name = f'{stu_exam_ticket_num}_{time_string}.pdf'

    print('开始生成文件')
    os.system('pwd')
    # pdf_path = generate_pdf(student_info)

    endpoint = os.environ.get('OSS_ENDPOINT', 'oss-cn-hangzhou.aliyuncs.com')
    bucket_name = os.environ.get('OSS_BUCKET', 'va-pics')
    auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())
    bucket = oss2.Bucket(auth, endpoint, bucket_name)
    bucket.put_object_from_file(f'vision-cup-report/{oss_file_name}', pdf_path)
    return jsonify({"status": "ok", "url": f'https://{bucket_name}.oss-cn-hangzhou.aliyuncs.com/vision-cup-report/{oss_file_name}'})

"""
根据传入的参数，显示对应的结果
"""
@app.route("/api/v1/get_exam_info", methods=['POST'])
def get_exam_info():
    requests_param = request.get_json()
    if requests_param is None:
        return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400

    logging.info(f"Received parameters: {requests_param}")

    # TODO 检查参数有效性
    student_name = requests_param['studentName']
    student_name = student_name.replace('-黑金会员','').replace('-白金会员','').replace('-铂金会员','').replace('_','').replace('.','')
    student_id = requests_param['examCertNo']
    test_name = requests_param['examPaperNo']
    subject, level = test_name.split('_')
    ans_list = requests_param['examResult']
    exam_sort = requests_param['examSort']
    cup_year = requests_param['cup_year']
    cup_round = requests_param['cup_round']
    exam_answer_content = requests_param.get('examAnswerContent', '')

    logging.info(f"Subject: {subject}, Level: {level}")

    logging.info(f"Loading JSON data from file: data/{cup_year}/{cup_round}/questions_{cup_round}_2025.json")

    # Load JSON data
    try:
        with open(f'data/{cup_year}/{cup_round}/questions_{cup_round}_2025.json') as file:
            all_questions = json.load(file)
        logging.info(f"Successfully loaded JSON data. Total questions: {len(all_questions)}")
    except FileNotFoundError:
        logging.error(f"JSON file not found: data/{cup_year}/{cup_round}/questions_{cup_round}_2025.json")
        return jsonify({'status': 'error', 'message': 'Question data not found'}), 404
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from file")
        return jsonify({'status': 'error', 'message': 'Error reading question data'}), 500

    # Filter questions for this exam
    exam_questions = [q for q in all_questions if q['Subject'] == subject and 
                      q['Level'] == level and
                      q['Year'] == cup_year and q['Round'] == cup_round]
    logging.info(f"Filtered questions for exam. Total exam questions: {len(exam_questions)}")

    # Initialize summary
    summary = {
        'student_name': student_name,
        'student_id': student_id,
        'ans_list': ans_list,
        'xueke': test_name,
        'cup_round': cup_round
    }

    # Calculate number of topics
    topics = set(q['Topic'] for q in exam_questions)
    summary['num_of_topics'] = len(topics)
    logging.info(f"Number of unique topics: {summary['num_of_topics']}")

    # Process exam results
    topic_results = defaultdict(lambda: {'correct': 0, 'total': 0, 'subtopics': defaultdict(list)})
    
    for i, (q, result, sort_order) in enumerate(zip(exam_questions, ans_list, exam_sort)):
        logging.info(f"Processing question {i+1}: Topic: {q['Topic']}, Result: {result}, Sort Order: {sort_order}")
        topic = q['Topic']
        subtopic = q['Subtopic']
        is_correct = result == '2'
        
        topic_results[topic]['total'] += 1
        if is_correct:
            topic_results[topic]['correct'] += 1
        
        subtopic_index = (sort_order - 1) // 3
        topic_results[topic]['subtopics'][subtopic_index].append((q, is_correct))

    logging.info(f"Processed exam results. Number of topics: {len(topic_results)}")
    logging.info(f"Topic results: {topic_results}")

    # Generate summary entries
    subtopic_keys = []
    for i, (topic, data) in enumerate(topic_results.items(), 1):
        accuracy = round(data['correct'] / data['total'] * 100)
        summary[f'topic{i}'] = topic
        summary[f'topic{i}_accuracy'] = accuracy
        logging.info(f"Topic {i}: {topic}, Accuracy: {accuracy}%")

        for j, (subtopic_index, questions) in enumerate(data['subtopics'].items(), 1):
            subtopic_key = f'topic{i}_{j}'
            subtopic_keys.append(subtopic_key)
            
            # Use topic name if all subtopics are None or empty
            subtopic_names = set(q['Subtopic'] for q, _ in questions if q['Subtopic'])
            if not subtopic_names:
                summary[subtopic_key] = topic
            else:
                summary[subtopic_key] = ' / '.join(subtopic_names)
            
            logging.info(f"Subtopic {subtopic_key}: {summary[subtopic_key]}")

            comments = []
            mistakes = []

            for question, is_correct in questions:
                if is_correct:
                    comment = question['Comment_Correct']
                else:
                    comment = question['Comment_Wrong']
                    mistakes.append(f"Q{question['Question Number']}")
                
                if comment and not comment.endswith('；') and not comment.endswith('。'):
                    comment += '；'
                if comment:
                    comments.append(comment)

            combined_comment = ''.join(comments).rstrip('；') + '。' if comments else ""
            # Apply the replacements
            combined_comment = combined_comment.replace("学生", summary['student_name'] + "同学").replace("XXX", summary['student_name']).replace("。。","。")
            summary[f'{subtopic_key}_comment'] = combined_comment

            mistakes_comment = '错题：' + ', '.join(mistakes) if mistakes else '错题：无'
            # Apply the replacements to mistakes comment as well
            mistakes_comment = mistakes_comment.replace("学生", summary['student_name'] + "同学").replace("XXX", summary['student_name']).replace("。。","。")
            summary[f'{subtopic_key}_comment_mistakes'] = mistakes_comment
            
            # Log the generated comment for each subtopic
            logging.info(f"Subtopic {subtopic_key} comment: {summary[f'{subtopic_key}_comment'][:100]}...")  # Log first 100 characters
            logging.info(f"Subtopic {subtopic_key} mistakes: {summary[f'{subtopic_key}_comment_mistakes']}")

    # Define section1_keys and section2_keys
    total_subtopics = len(subtopic_keys)
    mid_point = (len(topic_results) + 1) // 2  # This ensures a fair split for odd numbers of topics
    summary['section1_keys'] = subtopic_keys[:mid_point]
    summary['section2_keys'] = subtopic_keys[mid_point:]

    # Calculate section1_mark and section2_mark
    section1_correct = sum(topic_results[topic]['correct'] for topic in list(topic_results.keys())[:mid_point])
    section1_total = sum(topic_results[topic]['total'] for topic in list(topic_results.keys())[:mid_point])
    summary['section1_mark'] = round(section1_correct / section1_total * 100, 2) if section1_total > 0 else 0

    section2_correct = sum(topic_results[topic]['correct'] for topic in list(topic_results.keys())[mid_point:])
    section2_total = sum(topic_results[topic]['total'] for topic in list(topic_results.keys())[mid_point:])
    summary['section2_mark'] = round(section2_correct / section2_total * 100, 2) if section2_total > 0 else 0

    logging.info(f"Section 1 Mark: {summary['section1_mark']}%")
    logging.info(f"Section 2 Mark: {summary['section2_mark']}%")

    logging.info(f"Generated summary. Number of subtopics: {total_subtopics}")
    logging.info(f"Summary keys: {summary.keys()}")
    logging.info(f"Topic accuracies: {[summary.get(f'topic{i}_accuracy') for i in range(1, summary['num_of_topics'] + 1)]}")
    logging.info(f"Topics: {list(topic_results.keys())}")
    logging.info(f"Section 1 topics: {list(topic_results.keys())[:mid_point]}")
    logging.info(f"Section 2 topics: {list(topic_results.keys())[mid_point:]}")

    # Continue with the rest of your existing code...
    import Codes.gen_text as gt
    import Codes.saidao as sd
    import Codes.spider_plot as sp
    import Codes.get_grades as gg
    _ = gt.gen_breakdowns(summary)
    _ = sd.generate_saidao(test_name, summary)
    _ = sp.generate_spider_plot(summary)
    _ = gt.gen_main(summary)
    if ('wenke_lv2' in test_name) and (cup_year == '2024') and (cup_round != 'R3'):
        _ = gt.gen_main_wenke(summary)
    _ = gg.get_grades(test_name, summary)
    _ = gt.gen_summary(summary)
    return jsonify({"grade" : gg.get_grades_str(test_name, summary)})


"""
生成PDF
"""
def generate_pdf(summary):
    student_name = summary['student_name']
    student_id = summary['student_id']
    test_name = summary['xueke']
    ans_list = summary['ans_list']
    # cup_year = summary.get('cup_year')
    # cup_round = summary.get('cup_round')

    # Ensure these values are present in the summary
    # if not all([cup_year, cup_round]):
    #     raise ValueError("Missing cup_year or cup_round in summary")

    xueke_dict = {
        "bio_lv1": "生物 Level 1", "bio_lv2": "生物 Level 2",
        "chem_lv1": "化学 Level 1", "chem_lv2": "化学 Level 2",
        "eco_lv1": "经济 Level 1", "eco_lv2": "经济 Level 2",
        "maths_lv1": "数学 Level 1", "maths_lv2": "数学 Level 2",
        "phy_lv1": "物理 Level 1", "phy_lv2": "物理 Level 2",
        "wenke_lv1": "文社科 Level 1", "wenke_lv2": "文社科 Level 2"
    }
    summary['xueke'] = xueke_dict.get(test_name, test_name)

    # The topic and subtopic information is already in the summary
    # We don't need to recalculate it here

    import Codes.gen_text as gt
    import Codes.saidao as sd
    import Codes.spider_plot as sp
    import Codes.get_grades as gg

    _ = gt.gen_breakdowns(summary)
    _ = sd.generate_saidao(test_name, summary)
    _ = sp.generate_spider_plot(summary)
    _ = gt.gen_main(summary)
    # if ('wenke_lv2' in test_name) and (cup_year == '2024') and (cup_round != 'R3'):
    #     _ = gt.gen_main_wenke(summary)
    _ = gg.get_grades(test_name, summary)
    _ = gt.gen_summary(summary)

    os.system(f'xelatex -interaction=nonstopmode {student_id}')
    os.system(f'mv {student_id}.pdf exam/output/')
    return f"exam/output/{student_id}.pdf"

"""
根据传入参数，下载销售计划的PDF文件
"""
@app.route("/api/v1/sales_plan_down_pdf", methods=['POST'])
def sales_plan_down_pdf():
    requests_param = request.get_json()
    if requests_param is None:
        return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400

    logging.info(f"Received sales plan parameters: {requests_param}")

    # Parse the content if it's a string
    if isinstance(requests_param.get('content', ''), str):
        try:
            content = json.loads(requests_param.get('content', '{}'))
        except json.JSONDecodeError:
            return jsonify({'status': 'error', 'message': 'Invalid content JSON'}), 400
    else:
        content = requests_param.get('content', {})
        
    themeId = requests_param.get('theme', '')
    
    # Extract parameters for file naming
    plan_name = content.get('name', 'unnamed_plan')
    consultant = content.get('consultant', 'unknown_consultant')
    
    # Remove any special characters that might cause issues in filenames
    plan_name = plan_name.replace('/', '_').replace('\\', '_').replace(' ', '_')
    consultant = consultant.replace('/', '_').replace('\\', '_').replace(' ', '_')
    
    logging.info(f"Processing sales plan '{plan_name}' for consultant: {consultant}")
    
    # Generate the PDF by passing the entire JSON data
    pdf_path = generate_sales_plan_pdf(content, themeId)
    
    # Create a timestamp-based filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    pdf_filename = f"sales_plan_{timestamp}.pdf"
    oss_file_name = pdf_filename
    
    logging.info(f"Generated PDF at {pdf_path}, preparing to upload to OSS")
    
    # Upload to OSS
    # endpoint = os.environ.get('OSS_ENDPOINT', 'oss-cn-hangzhou.aliyuncs.com')
    # bucket_name = os.environ.get('OSS_BUCKET', 'va-pics')
    # auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())
    # bucket = oss2.Bucket(auth, endpoint, bucket_name)
    
    # Upload to sales-plan directory
    # bucket.put_object_from_file(f'sales-plan/{oss_file_name}', pdf_path)
    
    return jsonify({
        "status": "ok", 
        # "url": f'https://{bucket_name}.oss-cn-hangzhou.aliyuncs.com/sales-plan/{oss_file_name}'
    })

if __name__ == '__main__':
    app.run(
            # host='0.0.0.0',
            host='127.0.0.1',
            port=6666,
            # debug=True
            )

