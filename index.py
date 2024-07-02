import streamlit as st
from utils import draw_script
import requests
from streamlit_js_eval import streamlit_js_eval
from streamlit_pills import pills
import io
import cloudinary
import cloudinary.uploader
import cloudinary.api
import time

# Configuration       
cloudinary.config( 
    cloud_name = "dvex4tfg6", 
    api_key = "219979165586892", 
    api_secret = "Uzr-crPqTZ7GQrVl1y5ZrsXLNII", # Click 'View Credentials' below to copy your API secret
    secure=True
)

# result = cloudinary.api.resources(type="upload", max_results=100)  # 可以根据需要调整 max_results

# Set page config
st.set_page_config(page_title='Image Pixels',
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
    
if 'split_width_and_height' not in st.session_state:
    st.session_state.split_width_and_height = True

if 'show_color' not in st.session_state:
    st.session_state.show_color = True

if 'pixel_rotate_moed' not in st.session_state:
    st.session_state.pixel_rotate_moed = False

page_select = st_navbar(    
                 pages=["ArtPlay Image Pixels"],
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
        上传图片,调整参数去感受不同的效果吧! 本交互由 p5.js 构建, 基础使用可参考 <a href="https://p5refs.streamlit.app/" target="_blank">速查手册</a> , 此外可去 <a href="https://artplay-code.streamlit.app/" target="_blank">ArtPlay Code</a> 进一步学习
        </div>
        """,
        unsafe_allow_html=True
    )

if len(st.session_state.image_hash_set) == 0:
    init_image = "http://res.cloudinary.com/dvex4tfg6/image/upload/v1719906825/ArtPlay_demo.jpg"
else:
    init_image = None

c1,c2 = st.columns([1,5])

with c1:
    with st.expander("像素参数",expanded=True):
        pixel_shape = pills("像素形状", ["矩形","圆形","三角形","随机"], key="pills_interactive",index=0)

        if pixel_shape == "矩形":
            pixel_step = st.slider("像素间距", 3, 100, 20, 1)
        else:
            pixel_step = st.slider("像素间距", 3, 100, 45, 1)

        if ((pixel_shape == "矩形" or pixel_shape == "圆形")) and st.session_state.split_width_and_height :
            cc1,cc2 = st.columns(2)
            if pixel_shape == "圆形":
                pixel_shape = "胶囊"
                with cc1:
                    pixel_size = st.slider("像素半径", 1, 100, 20, 1)
                with cc2:
                    pixel_size_2 = st.slider("像素轴长", 1, 100, 1, 1)
            else:
                with cc1:
                    pixel_size = st.slider("像素宽度", 1, 100, 5, 1)
                with cc2:
                    pixel_size_2 = st.slider("像素长度", 1, 100, 15, 1)
            random_point_num = 0
        elif pixel_shape == "随机":
            cc1,cc2 = st.columns(2)
            with cc1:
                pixel_size = st.slider("像素大小", 1, 100, 20, 1)
            with cc2:
                random_point_num = st.slider("随机点数", 1, 20, 4, 1)
            pixel_size_2 = 0
        else:
            pixel_size = st.slider("像素大小", 1, 100, 40, 1)
            pixel_size_2 = 0
            random_point_num = 0
        pixel_opacity = st.slider("像素透明度", 0, 255, 255, 1)
        roate_degree = st.slider("像素旋转角度", 0, 360, 15, 1)
    with st.expander("交互参数"):
        damping = st.slider("像素灵敏度", 0.01, 0.2, 0.05, 0.01)
        if st.session_state.pixel_rotate_moed:
            force = st.slider("交互力度", 0, 20000, 0, 500,key="force")
        else:
            force = st.slider("交互力度", 0, 20000, 3000, 500,key="force_default")
    with st.expander("进阶参数"):
        show_color = st.toggle("显示颜色", True,key="show_color")
        if not show_color:
            gray_filter = st.slider("灰度过滤", 0, 255, 250, 1)
        else:
            gray_filter = 255
        color_angle_mode  = st.toggle("颜色角度", True)
        split_width_and_height = st.toggle("区分长宽", False,key="split_width_and_height")
        wave_mode = st.toggle("波动模式", False)
        if wave_mode:
            wave_size = st.slider("波动大小", 1, 50, 20, 1)
        else:
            wave_size = 0
        pixel_rotate_moed = st.toggle("像素旋转", False,key="pixel_rotate_moed")
        if pixel_rotate_moed:
            pixel_roatate_speed = st.slider("旋转速度", 0, 30, 5, 1,help="点击屏幕开始和暂停旋转")
        else:
            pixel_roatate_speed = 0
        #gif_seconds = st.slider("GIF时长", 1, 10, 3, 1)
    height = streamlit_js_eval(js_expressions='screen.height', key = 'SCR1',want_output = True)    
    
with c2:
    try:
        play = st.container(height=(height - 430))
    except:
        play = st.container(height=540)
    note = st.empty()
    
    success = False
    # add input for image url

    
    uploaded_file = st.file_uploader("自定义上传图片", type=['jpg', 'png', 'jpeg','webp'])

    input_url = st.text_input("或者输入图片URL", value="",placeholder="输入图片URL (https开头) , 并按回车键确认")
    
    if input_url:
        success = True
        init_image = None

    if uploaded_file:
        input_url = None
        if uploaded_file.size > 2*1024*1024:
            # 使用 PIL 做压缩处理 不改变图片长宽比
            from PIL import Image 
            img = Image.open(uploaded_file)
            img = img.convert('RGB')
            img.thumbnail((2048, 2048)) # 限制图片最大边长为 2048
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG")
            buffer.seek(0)  # 重置 buffer 指针到起始位置
        else:
            buffer = uploaded_file.read()
        
        if hash(uploaded_file.name) not in st.session_state.image_hash_set:
            try:                
                with st.spinner("图片上传中..."):
                    # https://console.cloudinary.com/pm/c-4e2c8dff8262ebfec0ff3aaea4dccd/getting-started
                    # https://console.cloudinary.com/pm/c-4e2c8dff8262ebfec0ff3aaea4dccd/media-explorer
                    # https://console.cloudinary.com/pm/c-4e2c8dff8262ebfec0ff3aaea4dccd/developer-dashboard
                    # Upload an image
                    upload_result = cloudinary.uploader.upload(file=buffer,
                                                               public_id= 'ArtPlay_' + uploaded_file.name.split(".")[0])
                    print(upload_result)
                    url = upload_result["secure_url"]
                    success = True
                    init_image = None
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
    if input_url:
        url = input_url
    note.caption("点击画布后 , 按键盘R键重绘画面 , 按键盘P键暂停/继续动画 , 按键盘S键保存当前图片 , 按键盘G键保存3秒的GIF")
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
    let wave = $$wave_mode$$;
    let wave_size = $$wave_size$$;
    let pixel_opacity = $$pixel_opacity$$;
    let color_angle_mode = $$color_angle_mode$$;
    let pixel_rotate_moed = $$pixel_rotate_moed$$;
    let pixel_roatate_speed = $$pixel_roatate_speed$$;
    let start_pixel_rotate = false;
    let pixel_roatate_time = 0;
    let text_for_image = "Create by ArtPlay";
    let text_for_image_font = "Playwrite US Trad";
    let text_for_image_color = "#444444";
    let random_point_num = $$random_point_num$$;

    let pixel_size_2 = $$pixel_size_2$$;
    let split_width_and_height = $$split_width_and_height$$;

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
        pixel_roatate_time = 0;
    }

    function setup() {
    // max width: windowWidth
    // max height: $$GoodHeight$$

    // fit image to window within max height and max width
    let ratio = img.width / img.height;
    if (img.width > windowWidth) {
        img.width = windowWidth;
        img.height = img.width / ratio;
    }
    if (img.height > $$GoodHeight$$) {
        img.height = $$GoodHeight$$;
        img.width = img.height * ratio;
    }
    

    img.resize(img.width, img.height);

    createCanvas(img.width, img.height);

    img.loadPixels();     
    init_particles();   

    }

    function draw() {
    background(background_color);
    for (let i = 0; i < particles.length; i++) {
        particles[i].update();
        particles[i].display();
    }

    if (start_pixel_rotate){
        pixel_roatate_time += 1;
    }
    // 水印签名
    textAlign(CENTER, CENTER);
    textSize(height/40);
    textFont(text_for_image_font);
    stroke(255);
    strokeWeight(2);
    fill(text_for_image_color);
    text(text_for_image, width/2, height * 0.95);
    }
    

    function particle(target,color) {
    this.s = createVector(random(width), random(height));
    this.v = createVector(0,0);
    this.a = createVector(0,0);
    this.target = target;
    this.color = [color[0],color[1],color[2],pixel_opacity];
    this.random_points = [];
    for (let i = 0; i < random_point_num; i++) {
    this.random_points.push([random(0,pixel_size),random(0,pixel_size)]);
    }

    this.update = () => {
        let mouse = createVector(mouseX, mouseY);
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
        translate(this.s.x,this.s.y);
        if (color_angle_mode){
            init_angle = get_color_by_rgb(this.color[0],this.color[1],this.color[2]);
        }else{
            init_angle = 0;
        }
        if (start_pixel_rotate && pixel_rotate_moed){
            rotate(($$roate_degree$$ + init_angle + pixel_roatate_time/10 * pixel_roatate_speed ) * PI / 180);
        }else{
            rotate(($$roate_degree$$ + init_angle + pixel_roatate_time/10 * pixel_roatate_speed ) * PI / 180);
        }
        if (pixel_shape == "矩形") {
            rectMode(CENTER);
            noStroke();
            if (split_width_and_height) {
            rect(0,0, pixel_size,pixel_size_2);
            }else{
            rect(0,0, pixel_size,pixel_size);
            }
            textAlign(CENTER, CENTER);
            //text(this.color[0] + "," + this.color[1] + "," + this.color[2], 0, 0);
            //text(init_angle, 0, 0);
        }else if (pixel_shape == "圆形") {
            noStroke();
            circle(0,0, pixel_size);
        }else if (pixel_shape == "三角形") {
            noStroke();
            let points = get_triangle_points(pixel_size);
            triangle(points[0][0],points[0][1],points[1][0],points[1][1],points[2][0],points[2][1]);
        }else if (pixel_shape == "线圆") {
            rectMode(CENTER);
            noStroke();
            rect(0,0, pixel_size,pixel_size_2);
            circle(-pixel_size/2,0, pixel_size_2/2);
            circle(pixel_size/2,0, pixel_size_2/2);
        }
        else if (pixel_shape == "胶囊") {
            rectMode(CENTER);
            noStroke();
            rect(0,0, pixel_size,pixel_size_2+0.1); // 0.1 是为了避免出现间隙
            arc(0,pixel_size_2/2, pixel_size, pixel_size, 0, PI);
            arc(0,-pixel_size_2/2, pixel_size, pixel_size, PI, TWO_PI);
        }
        else{
            noStroke();
            beginShape();
            for (let i = 0; i < this.random_points.length; i++) {
            vertex(this.random_points[i][0],this.random_points[i][1]);
            }
            endShape(CLOSE);
        }
        pop();
    }

    }
    
    // get_triangle_points 函数
    function get_triangle_points(size){
        h = size * 3**0.5 / 2;
        return [[0,-h/2],[size/2,h/2],[-size/2,h/2]];
    }

    // 基于RGB区分成白红橙黄绿青蓝紫黑 9 个区间 返回 对应角度 0  40 80 120 160 200 240 280 320
    function get_color_by_rgb(r,g,b){
        let max = Math.max(r,g,b);
        let min = Math.min(r,g,b);
        let delta = max - min;
        let angle = 0;
        if (max == 0){
            return angle;
        }
        if (max == r && g >= b){
            angle = 40*(g - b)/delta;
        }else if (max == r && g < b){
            angle = 40*(g - b)/delta + 240;
        }else if (max == g){
            angle = 40*(b - r)/delta + 80;
        }else if (max == b){
            angle = 40*(r - g)/delta + 160;
        }
        return angle;
    }
        
    
    // click mouse to start rotate and end rotate
    function mouseClicked() {
        if (start_pixel_rotate){
            start_pixel_rotate = false;
        }else{
            start_pixel_rotate = true;
        }
    }

    // 保存
    function keyPressed() {
    // 点击画面后按键盘G键 保存3秒的GIF
    if (key === 'g') {
    saveGif('mySketch', 3);
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
    script = script.replace("$$split_width_and_height$$",str(st.session_state.split_width_and_height).lower())
    script = script.replace("$$wave_mode$$",str(wave_mode).lower())
    script = script.replace("$$wave_size$$",str(wave_size))
    script = script.replace("$$color_angle_mode$$",str(color_angle_mode).lower())
    script = script.replace("$$pixel_rotate_moed$$",str(pixel_rotate_moed).lower())
    script = script.replace("$$pixel_roatate_speed$$",str(pixel_roatate_speed))
    script = script.replace("$$pixel_size_2$$",str(pixel_size_2))
    script = script.replace("$$random_point_num$$",str(random_point_num))
    
    try:
        script = script.replace("$$GoodHeight$$",str(height - 490))
    except:
        script = script.replace("$$GoodHeight$$",str(500))
        print("GoodHeight Error")
    with play:
        st.markdown("""
    <style>
    .center {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%; /* Ensure iframe takes full height of the container */
    }
    </style>
    """, unsafe_allow_html=True)
        try:
            draw_script(script,height = height - 490)
        except:
            draw_script(script,height = 500)
else:
    with play:
        _,c,_ = st.columns([5,6,1])
        with c:
            st.caption("  请先上传图片")