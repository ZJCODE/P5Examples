import streamlit.components.v1 as components

def get_html_content(script):

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playwrite+US+Trad:wght@100..400&display=swap" rel="stylesheet">
    <head>
        <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.4/p5.min.js"></script>
        <script>{script}</script>
        <meta charset="utf-8" />
        <style>
            html, body {{
                height: 100%;
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
        </style>
    </head>
    <body></body>
    </html>
    """
    
def draw_script(script,height=500):
        if 'createCanvas' not in script or 'function setup()' not in script:
            return components.html("请检查代码是否为P5.js代码")
        try:
            width_in_code = int(script.replace(" ","").split("createCanvas(")[1].split(",")[0])
            height_in_code = int(script.replace(" ","").split("createCanvas(")[1].split(",")[1].split(");")[0])
        except Exception as e:
            html = get_html_content(script=script)
            return components.html(html,height=height)

        html = get_html_content(script=script)

        return components.html(html, width=width_in_code, height=height_in_code)