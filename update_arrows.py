import glob
import re

for file_path in glob.glob('雅思阅读考试_Part*.html'):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # The issue in Part 2 and 3 is that the JS for `left-arrow` and `right-arrow` might have been stripped or was inside the "段落标签功能" block that was removed.
    # Let's check if left-arrow is in the content
    
    # We will just append the missing arrow navigation logic if it's missing, or rewrite it.
    # We can check what's at the end of the script tag.
    
    # Let's ensure the arrows have event listeners.
    arrow_js_1 = '''
            $('.left-arrow').on('click', function() {
                return false;
            });

            $('.right-arrow').on('click', function() {
                window.location.href = '雅思阅读考试_Part2.html';
            });
    '''
    arrow_js_2 = '''
            $('.left-arrow').on('click', function() {
                window.location.href = '雅思阅读考试_Part1.html';
            });

            $('.right-arrow').on('click', function() {
                window.location.href = '雅思阅读考试_Part3.html';
            });
    '''
    arrow_js_3 = '''
            $('.left-arrow').on('click', function() {
                window.location.href = '雅思阅读考试_Part2.html';
            });

            $('.right-arrow').on('click', function() {
                return false;
            });
    '''
    
    if file_path == '雅思阅读考试_Part1.html':
        arrow_js = arrow_js_1
    elif file_path == '雅思阅读考试_Part2.html':
        arrow_js = arrow_js_2
    else:
        arrow_js = arrow_js_3
        
    # We need to make sure the end of the script has these handlers.
    # We'll just replace the closing tag with these + closing tag, but first remove any existing `.left-arrow` or `.right-arrow` handlers to avoid duplicates.
    
    content = re.sub(r'\$\(\'\.left-arrow\'\)\.on\(\'click\',\s*function\(\)\s*\{.*?\}\);', '', content, flags=re.DOTALL)
    content = re.sub(r'\$\(\'\.right-arrow\'\)\.on\(\'click\',\s*function\(\)\s*\{.*?\}\);', '', content, flags=re.DOTALL)
    
    content = content.replace('        });\n    </script>', arrow_js + '\n        });\n    </script>')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Fixed arrows in {file_path}')
