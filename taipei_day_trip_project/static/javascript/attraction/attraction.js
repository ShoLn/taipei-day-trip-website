let attrac_id = window.location.pathname.split("/")[2]; //取得景點編號
let img_container = document.querySelector("div.c_img_container"); // 圖片容器div
let dot_container = document.querySelector("div.c_dot_container"); // 圓點容器

load_attrac_id();
async function load_attrac_id() {
    let res = await fetch(`/api/attraction/${attrac_id}`);
    let res_json = await res.json();
    let data = res_json.data;

    //創造圖片and圓點
    for (let i = 0; i < data.images.length; i++) {
        let img = document.createElement("img");
        img.classList.add("c_img");
        img.src = data.images[i];
        img_container.appendChild(img);
        let dot = document.createElement("button");
        dot.classList.add("c_dot");
        dot_container.appendChild(dot);
    }

    let imgs_array = Array.from(img_container.children); // 所有圖片 array
    let dots_node = document.querySelectorAll("button.c_dot"); // 所有園點 nodelist
    imgs_array[0].classList.add("current_img"); // 第一張圖片加入代表目前顯示圖片的class
    dots_node[0].classList.add("current_dot"); // 第一個圓點加入代表目前顯示圓點的class

    //輪播圖片按鈕功能
    let button_right = document.querySelector("button.c_right_button");
    button_right.addEventListener("click", (e) => {
        let current_img = document.querySelector("img.current_img"); // 目前顯示圖片
        let next_img = current_img.nextElementSibling; // 顯示圖片的下一張圖片
        if (next_img == null) {
            next_img = imgs_array[0];
        } // 若有下一張再往下
        current_img.classList.remove("current_img"); // 移除代表目前顯示圖片class
        next_img.classList.add("current_img"); // 下一張圖片加入代表現在顯示圖片的class
        let current_dot = document.querySelector("button.current_dot"); //現在圓點
        let next_dot = current_dot.nextElementSibling; // 下一個圓點
        if (next_dot == null) {
            next_dot = document.querySelectorAll("button.c_dot")[0];
        }
        current_dot.classList.remove("current_dot"); // 移除代表現在顯示圓點的class
        next_dot.classList.add("current_dot"); // 下一圓點加入代表現在圓點的class
    });

    let button_left = document.querySelector("button.c_left_button");
    button_left.addEventListener("click", (e) => {
        let current_img = document.querySelector("img.current_img");
        let prev_img = current_img.previousElementSibling;
        if (prev_img == null) {
            prev_img = imgs_array[imgs_array.length - 1];
        }
        current_img.classList.remove("current_img");
        prev_img.classList.add("current_img");
        let current_dot = document.querySelector("button.current_dot");
        let prev_dot = current_dot.previousElementSibling;
        if (prev_dot == null) {
            let dots = document.querySelectorAll("button.c_dot");
            prev_dot = dots[dots.length - 1];
        }
        current_dot.classList.remove("current_dot");
        prev_dot.classList.add("current_dot");
    });

    //輪播圖片右半邊資料載入
    let name = document.querySelector("div.name");
    name.innerText = data.name;
    let cate_mrt = document.querySelector("div.cate_mrt");
    cate_mrt.innerText = `${data.category} at ${data.mrt}`;
    let radios = document.querySelectorAll('input[name="time"]');
    //radio 變更金錢功能
    radios.forEach((radio) => {
        radio.addEventListener("change", (e) => {
            let radio_value = document.querySelector(
                'input[name="time"]:checked'
            ).value;
            let money = document.querySelector("div.money1");
            if (radio_value == "down") {
                money.innerText = "新台幣 2500 元";
            } else {
                money.innerText = "新台幣 2000 元";
            }
        });
    });

    //下半部資料載入
    let description = document.querySelector("div.description");
    description.innerText = data.description;
    let address1 = document.querySelector("div.address1");
    address1.innerText = data.address;
    let trans = document.querySelector("div.trans1");
    trans.innerText = data.transport;
}

//booking api
async function api_booking(method, data) {
    let res = await fetch("/api/booking", {
        method: method,
        headers: {
            "Content-Type": "application/json",
        },
        body: data,
    });
    res_json = await res.json();
    return res_json;
}
//開始預定行程按鈕設定
let start_booking = document.querySelector("form"); //開始預定行程表單
start_booking.addEventListener("submit", (e) => {
    let div_signout = document.querySelector("div.signout"); //登出按鈕
    //若沒登入
    if (!div_signout) {
        e.preventDefault();
        let pop_login = document.querySelector(".pop_outest"); //登入視窗
        pop_login.style.display = "flex";
    } else {
        //若有登入
        e.preventDefault();
        let tour_date = document.querySelector("input.date").value; //日期
        let tour_time = document.querySelector(
            'input[name="time"]:checked'
        ).value; //時間
        let tour_cost = document
            .querySelector("div.money1")
            .innerText.slice(4, 8); //費用

        data = JSON.stringify({
            tour_date: tour_date,
            tour_time: tour_time,
            tour_cost: tour_cost,
            attrac_id: attrac_id,
        });
        // 將資料用post api/booking 送到後端
        let res = api_booking("POST", data);
        res.then((res_json) => {
            if (res_json.ok) {
                location.href = "/booking";
            } else {
                //同一人同一天同個時段只能預約一次
                let div_book_error0 = document.querySelector("div.book_error0");
                div_book_error0.style.display = "flex";
                document.querySelector("div.book_error3").innerText =
                    res_json.message;
                let img_close = document.querySelector("div.book_error1 img");
                img_close.addEventListener("click", (e) => {
                    document.querySelector("div.book_error3").innerText = "";
                    div_book_error0.style.display = "none";
                });
            }
        });
    }
});
