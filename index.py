import streamlit as st
from utils import draw_script
import requests
from streamlit_js_eval import streamlit_js_eval
from streamlit_pills import pills

# Set page config
st.set_page_config(page_title='Image Particles',
                   page_icon='🎨', 
                   layout='wide',
                   initial_sidebar_state='collapsed')

from streamlit_navigation_bar import st_navbar

styles = {
    "nav": {
        "background-color": "white",
        "justify-content": "left",
    },
    "span": {
        "color": "white",
        "padding-left": "48px",
    },
    "active": {
        "background-color": "white",
        "color": "#f58025",
        "font-size": "25px",
        "font-weight": "bold",
    }
}

if 'image_hash_set' not in st.session_state:
    st.session_state.image_hash_set = dict()

page_select = st_navbar(    
                 pages=["ArtPlay Image Particles"],
                 styles = styles,
                 options={"use_padding": False,"show_menu": False,"show_sidebar": False}
                 )

st.markdown(
        """
        <style>
        .note {
            width: 100%;
            background-color: #ffffff; /* White background */
            text-align: left;
            padding: 10px 0;
            color: #888888; /* Black text */
            font-size: 14px; /* Font size */
        }
        .note a {
            /* text-decoration: none; Remove underline */
            color: #888888; /* Set link color */
        }
        </style>
        <div class="note">
        上传图片,调整参数去感受不同的效果吧! 本交互由 p5.js 构建, 基础使用可参考 <a href="https://p5refs.streamlit.app/" target="_blank">速查手册</a> , 此外可去 <a href="https://artplay.streamlit.app/" target="_blank">ArtPlay</a> 进一步学习
        </div>
        """,
        unsafe_allow_html=True
    )

if len(st.session_state.image_hash_set) == 0:
    init_image = "https://s2.loli.net/2024/06/28/mdHhleWiyjwEtF6.jpg"
else:
    init_image = None

c1,c2 = st.columns([1,5])

with c1:
    with st.expander("像素参数"):
        pixel_shape = pills("像素形状", ["矩形","圆形","三角形"], key="pills_interactive",index=0)
        pixel_step = st.slider("像素间距", 5, 50, 35, 1)
        if pixel_shape == "矩形":
            cc1,cc2 = st.columns(2)
            with cc1:
                pixel_size = st.slider("像素大小(长)", 1, 200, 40, 1)
            with cc2:
                pixel_size_2 = st.slider("像素大小(宽)", 1, 200, 40, 1)
        else:
            pixel_size = st.slider("像素大小", 1, 200, 40, 1)
        pixel_opacity = st.slider("像素透明度", 0, 255, 75, 1)
        roate_degree = st.slider("像素旋转角度", 0, 360, 25, 1)
    with st.expander("交互参数"):
        damping = st.slider("像素灵敏度", 0.01, 0.2, 0.05, 0.01)
        force = st.slider("交互力度", 0, 20000, 3000, 1000)
    with st.expander("其他参数"):
        show_color = st.toggle("显示颜色", True)
        if not show_color:
            gray_filter = st.slider("灰度过滤", 0, 255, 255, 1)
        else:
            gray_filter = 255
    height = streamlit_js_eval(js_expressions='screen.height', key = 'SCR1',want_output = True)    
    
with c2:
    try:
        play = st.container(height=(height - 450))
    except:
        play = st.container(height=540)
    note = st.empty()
uploaded_file = st.file_uploader("自定义上传图片", type=['jpg', 'png', 'jpeg'])

# 判断 uploaded_file 的大小 不能超过 5MB 如果超过做压缩处理
if uploaded_file:
    if uploaded_file.size > 5*1024*1024:
        st.error("上传图片不能超过 5MB")
        uploaded_file = None

# 使用requests post上传图片
# https://doc.sm.ms/#api-User
# https://sm.ms/home/
url = "https://sm.ms/api/v2/upload"
headers = {'Authorization': "LF743DhFsJMlBSkTIX5I7hqqDUvKOdzh"}
success = False
if uploaded_file:
    if hash(uploaded_file.name) not in st.session_state.image_hash_set:
        files = {'smfile': uploaded_file.read()}
        try:
            with st.spinner("图片上传中..."):
                response = requests.post(url, headers=headers, files=files)
                if response.json()['code'] == "image_repeated":
                    url = response.json()['images']
                    success = True
                    init_image = None
                    # add url to hash set
                    st.session_state.image_hash_set[hash(uploaded_file.name)] = url
                elif response.json()['code'] == "success":
                    url = response.json()['data']['url']
                    delete_url = response.json()['data']['delete']
                    success = True
                    init_image = None
                    # add url to hash set
                    st.session_state.image_hash_set[hash(uploaded_file.name)] = url
                else:
                    st.error(f"图片上传失败 稍后再试")
        except Exception as e:
            st.error(f"图片上传失败 稍后再试")
            st.error(e)
    else:
        url = st.session_state.image_hash_set[hash(uploaded_file.name)]
        success = True
        init_image = None
if success or init_image:
    if init_image:
        url = init_image
    note.caption("点击画面后按键盘G键保存2秒的GIF，按键盘S键保存当前图片，按键盘P键暂停/继续动画，按键盘R键重绘画面")
    script = """
    
    let img;
    let pixel_shape = "$$pixel_shape$$";
    let step = $$pixel_step$$;
    let pixel_size = $$pixel_size$$;
    let show_color = $$show_color$$;
    let damping = $$damping$$;
    let force = $$force$$;
    let filter_threshold = $$gray_filter$$;
    let background_color = "#ffffff"; // 背景颜色
    let wave = false;
    let wave_size = 1;
    let pixel_opacity = $$pixel_opacity$$;

    let pixel_size_2 = $$pixel_size_2$$;

    function preload() {
    // 加载图片
    img = loadImage('$$image_url$$');
    }
    
    
    function init_particles(){
        particles = [];
        for (let i = 0; i < img.width; i += step) {
            for (let j = 0; j < img.height; j += step) {
            let color = img.get(i, j);
            let img_gray = color[0]*0.299 + color[1]*0.587 + color[2]*0.114;
            if (img_gray <= filter_threshold){
                particles.push(new particle( createVector(i,j),img.get(i,j))); 
            }
        }
        }
    }

    function setup() {
    createCanvas(windowWidth,$$GoodHeight$$);
    let img_ratio = img.width/img.height;
    let canvas_ratio = windowWidth/height;
    if (img_ratio > canvas_ratio){
        img.resize(windowWidth,0);
    }else{
        img.resize(0,height);
    }
    img.loadPixels();     
    init_particles();   
    }

    function draw() {
    background(background_color);
    for (let i = 0; i < particles.length; i++) {
        particles[i].update();
        particles[i].display();
    }
    }
    

    function particle(target,color) {
    this.s = createVector(random(width) - ( width/2 - 25 - img.width/2 ), random(height));
    this.v = createVector(0,0);
    this.a = createVector(0,0);
    this.target = target;
    this.color = [color[0],color[1],color[2],pixel_opacity];

    this.update = () => {
        let mouse = createVector(mouseX - ( width/2 - img.width/2 ), mouseY);
        let mouseVec = p5.Vector.sub( mouse, this.s );
        let d = p5.Vector.mag(mouseVec);
        if (wave){
            mouseVec.mult( - force/pow(d, 2) - force/pow(d, 2)*sin(d/wave_size));
        }else{
            mouseVec.mult( - force/pow(d, 2));
        }
        this.a.add( mouseVec );
        this.a.add( p5.Vector.sub( this.target, this.s ) );
        this.v.add( p5.Vector.mult( this.a, damping) );
        this.s.add( p5.Vector.mult( this.v, damping) );

        this.a.mult(0);
        this.v.mult(0.9);
    }

    this.display = () => {
        if (show_color){
            stroke(this.color);
            fill(this.color); // 使用颜色属性
        }else{
            gray = this.color[0]*0.299 + this.color[1]*0.587 + this.color[2]*0.114;
            stroke(gray,pixel_opacity);
            fill(gray,pixel_opacity); // 使用颜色属性
        }
        
        push();
        translate(this.s.x + ( width/2 - img.width/2) ,this.s.y);
        // 30 度旋转
        rotate($$roate_degree$$ * PI / 180);
        if (pixel_shape == "矩形") {
            rect(0,0, pixel_size,pixel_size_2);
        }else if (pixel_shape == "圆形") {
            circle(0,0, pixel_size);
        }else if (pixel_shape == "三角形") {
            let points = get_triangle_points(pixel_size);
            triangle(points[0][0],points[0][1],points[1][0],points[1][1],points[2][0],points[2][1]);
        }else{
            rect(0,0, pixel_size,pixel_size_2);
        }
        pop();
    }

    }
    
    // get_triangle_points 函数
    function get_triangle_points(size){
        h = size * 3**0.5 / 2;
        return [[0,-h/2],[size/2,h/2],[-size/2,h/2]];
    }
    
    // 保存
    function keyPressed() {
    // 点击画面后按键盘G键 保存2秒的GIF
    if (key === 'g') {
    saveGif('mySketch', 2);
    }
    // 点击画面后按键盘S键 保存当前图片
    if (key === 's') {
    saveFrames('frame', 'png', 1, 1);
    }
    if (key === 'p') {
        if (isLooping()) {
            noLoop();
        } else {
            loop();
        }
    }
    // 按下键盘 r 重绘画面
    if (key === 'r') {
        init_particles()
    }
    }
    
    """
    script = script.replace("$$image_url$$",url)
    script = script.replace("$$pixel_step$$",str(pixel_step))
    script = script.replace("$$pixel_size$$",str(pixel_size))
    script = script.replace("$$damping$$",str(damping))
    script = script.replace("$$force$$",str(force))
    script = script.replace("$$gray_filter$$",str(gray_filter))
    script = script.replace("$$show_color$$",str(show_color).lower())
    script = script.replace("$$roate_degree$$",str(roate_degree))
    script = script.replace("$$pixel_shape$$",pixel_shape)
    script = script.replace("$$pixel_opacity$$",str(pixel_opacity))
    if pixel_shape == "矩形":
        script = script.replace("$$pixel_size_2$$",str(pixel_size_2))
    
    try:
        script = script.replace("$$GoodHeight$$",str(height - 490))
    except:
        script = script.replace("$$GoodHeight$$",str(500))
        print("GoodHeight Error")
    with play:
        try:
            draw_script(script,height = height - 490)
        except:
            draw_script(script,height = 500)
else:
    with play:
        _,c,_ = st.columns([5,6,1])
        with c:
            st.caption("  请先上传图片")