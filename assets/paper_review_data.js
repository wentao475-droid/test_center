window.paperReviewStore = (function () {
    var papers = {
        "NUMK2026131629": {
            paperId: "NUMK2026131629",
            examName: "2026年牛剑试点模考",
            stepName: "STEP2",
            subject: "雅思口语",
            studentName: "王一博",
            studentId: "STU20260601001",
            candidateId: "NUMK2026131629",
            teacherName: "郭竞文",
            updatedAt: "2026-06-04 10:30",
            totalScore: "9.0",
            duration: "00:13",
            scoreOptions: ["5.5", "6.0", "6.5", "7.0", "7.5", "8.0", "8.5", "9.0"],
            tabs: ["试卷1", "试卷2", "试卷3", "试卷4"],
            activeTab: "试卷4",
            questions: [
                {
                    id: "part1",
                    title: "Part 1: Introduction & Interview",
                    prompt: "Let's talk about your hometown. Where is your hometown? What do you like most about it? Is there anything you dislike about it?",
                    cuePoints: [],
                    answerLabel: "学生作答内容",
                    transcript: "My hometown is Beijing, which is the capital of China. What I like most about it is the convenient transportation system and the rich historical culture. However, the traffic congestion during rush hours is something I really dislike.",
                    trace: "录音时长 2m 48s，语速稳定，出现 2 次长停顿。",
                    suggestedScore: "7.0",
                    comment: "回答完整，表达自然，细节较具体；可继续加强复杂句式与词汇层次。",
                    tags: ["流利度", "词汇多样性"]
                },
                {
                    id: "part2",
                    title: "Part 2: Long Turn",
                    prompt: "Describe a memorable journey you have made.",
                    cuePoints: [
                        "where you went",
                        "how you traveled",
                        "why you went there",
                        "and explain why it is memorable"
                    ],
                    answerLabel: "学生作答内容",
                    transcript: "I would like to talk about a trip to Yunnan province that I took last summer. I went there with my best friends by plane. We chose Yunnan because of its stunning natural scenery and unique local culture. It was memorable because it was our first time traveling independently without our parents, and we saw the beautiful snow mountain which I will never forget.",
                    trace: "录音时长 4m 21s，结构清晰，结尾略仓促。",
                    suggestedScore: "7.5",
                    comment: "内容较充实，逻辑顺序清晰，个别细节可进一步展开，增强表现力。",
                    tags: ["内容组织", "语法准确性"]
                },
                {
                    id: "part3",
                    title: "Part 3: Discussion",
                    prompt: "Why do some people prefer traveling alone while others prefer traveling with friends? Do you think travel can change a person's attitude toward life?",
                    cuePoints: [],
                    answerLabel: "学生作答内容",
                    transcript: "Some people like traveling alone because it gives them more freedom and time to reflect on themselves, while others prefer traveling with friends because they can share the experience and feel safer. I definitely think travel can change a person's attitude toward life because it helps people understand different cultures and become more open-minded.",
                    trace: "录音时长 5m 51s，论证完整，语调自然。",
                    suggestedScore: "8.0",
                    comment: "观点明确，展开充分；若能增加更复杂的论证层次，整体说服力会更强。",
                    tags: ["逻辑论证", "观点拓展"]
                }
            ]
        }
    };

    function getPaper(paperId) {
        return papers[paperId] || papers["NUMK2026131629"];
    }

    return {
        getPaper: getPaper
    };
})();
