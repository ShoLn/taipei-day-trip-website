//信用卡格式設定
let credit_number = document.querySelectorAll("div.c2 input")[0];
credit_number.addEventListener("keypress", (e) => {
    if (credit_number.value.length < 19) {
        credit_number.value = credit_number.value
            .replace(/\W/gi, "")
            .replace(/(.{4})/g, "$1 ");
        return true;
    } else {
        return false;
    }
});
credit_number.addEventListener("keyup", (e) => {
    e.target.value = e.target.value.replace(/[^\d ]/g, "");
    return false;
});

//檢查使用者登入狀態
// api/user async function
async function api_user(method, data) {
    let res = await fetch("/api/user", {
        method: method,
        headers: {
            "Content-Type": "application/json",
        },
        body: data,
    });
    let res_json = await res.json();
    return res_json;
}

// api/booking async function
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

window.addEventListener("load", (e) => {
    let res = api_user("GET", null);
    res.then((res_json) => {
        // 若沒登入導向首頁
        if (res_json.null) {
            location.href = "/";
        } else {
            //若有登入使用 GET /api/booking 抓取已預定的行程資料
            let res = api_booking("GET", null);
            res.then((res_json) => {
                // 若有預定行程的資料 全部列出來
                if (res_json.data.attrac.length) {
                    //總價變數
                    total_price = 0;
                    // 創建預定行程node 並放入get response 資料
                    let div_s0 = document.querySelector("div.s0");
                    div_s0.innerText = `您好，${res_json.data.user.name}，待預定的行程如下：`;
                    res_json.data.attrac.forEach((att) => {
                        total_price += att.price;
                        let div_s1 = document.createElement("div");
                        div_s1.classList.add("s1");
                        let hr = document.createElement("hr");
                        let form = document.querySelector("form");
                        form.insertBefore(hr, form.children[1]);
                        form.insertBefore(div_s1, form.children[1]);
                        let img = document.createElement("img");
                        img.classList.add("attrac_img");
                        img.src = att.image;
                        div_s1.appendChild(img);
                        let div_s2 = document.createElement("div");
                        div_s2.classList.add("s2");
                        div_s1.appendChild(div_s2);
                        let div_attrac_name = document.createElement("div");
                        div_attrac_name.classList.add("s3");
                        div_attrac_name.innerText = `台北一日遊：${att.name}`;
                        div_s2.appendChild(div_attrac_name);
                        let div_s4_0 = document.createElement("div");
                        div_s4_0.classList.add("s4");
                        div_s2.appendChild(div_s4_0);
                        let div_date0 = document.createElement("div");
                        div_date0.classList.add("s5");
                        div_date0.innerText = "日期：";
                        div_s4_0.appendChild(div_date0);
                        let div_date1 = document.createElement("div");
                        div_date1.classList.add("s6");
                        div_date1.innerText = att.date;
                        div_s4_0.appendChild(div_date1);
                        let div_s4_1 = document.createElement("div");
                        div_s4_1.classList.add("s4");
                        div_s2.appendChild(div_s4_1);
                        let div_time_0 = document.createElement("div");
                        div_time_0.classList.add("s5");
                        div_time_0.innerText = "時間：";
                        div_s4_1.appendChild(div_time_0);
                        let div_time_1 = document.createElement("div");
                        div_time_1.classList.add("s6");
                        if (att.time == "up") {
                            div_time_1.innerText = "早上8點到12點";
                        } else {
                            div_time_1.innerText = "下午13點到17點";
                        }
                        div_s4_1.appendChild(div_time_1);
                        let div_s4_2 = document.createElement("div");
                        div_s4_2.classList.add("s4");
                        div_s2.appendChild(div_s4_2);
                        let div_price_0 = document.createElement("div");
                        div_price_0.classList.add("s5");
                        div_price_0.innerText = "費用：";
                        div_s4_2.appendChild(div_price_0);
                        let div_price_1 = document.createElement("div");
                        div_price_1.classList.add("s6");
                        div_price_1.innerText = `新台北 ${att.price} 元`;
                        div_s4_2.appendChild(div_price_1);
                        let div_s4_3 = document.createElement("div");
                        div_s4_3.classList.add("s4");
                        div_s2.appendChild(div_s4_3);
                        let div_address_0 = document.createElement("div");
                        div_address_0.classList.add("s5");
                        div_address_0.innerText = "地點：";
                        div_s4_3.appendChild(div_address_0);
                        let div_address_1 = document.createElement("div");
                        div_address_1.classList.add("s6");
                        div_address_1.innerText = att.address;
                        div_s4_3.appendChild(div_address_1);
                        let icon_delete = document.createElement("img");
                        icon_delete.classList.add("icon_delete");
                        icon_delete.src = "/static/image/icon/icon_delete.png";
                        // 註冊清除行程資料 按鈕事件
                        icon_delete.addEventListener("click", (e) => {
                            //刪除行程資料庫資料
                            delete_data = JSON.stringify({
                                booking_id: att.booking_id,
                            });
                            api_booking("DELETE", delete_data);
                            //刪除html畫面
                            icon_delete.parentElement.nextElementSibling.remove();
                            icon_delete.parentElement.remove();
                            //總價跟著減少
                            total_price -= att.price;
                            let div_total_price =
                                document.querySelector("div.confirm1");
                            div_total_price.innerText = `總價：新台幣 ${total_price} 元`;
                            //若刪到都沒行程資料顯示都沒行程資料
                            if (!document.querySelector("div.s1")) {
                                let form = document.querySelector("form");
                                form.style.display = "none";
                                let no_schedule =
                                    document.querySelector("div.no_schedule");
                                no_schedule.style.display = "block";
                                let div_n0 = document.querySelector("div.n0");
                                div_n0.innerText = `您好，${res_json.data.user.name}，待預定的行程如下：`;
                            }
                        });
                        div_s1.appendChild(icon_delete);
                    });
                    //姓名信箱資料代入input
                    let input_user_name = document.querySelector(
                        "div.u2 input[id='name']"
                    );
                    input_user_name.value = res_json.data.user.name;
                    let input_user_email = document.querySelector(
                        "div.u2 input[id='email']"
                    );
                    input_user_email.value = res_json.data.user.email;
                    //總價放入div
                    let div_total_price =
                        document.querySelector("div.confirm1");
                    div_total_price.innerText = `總價：新台幣 ${total_price} 元`;
                } else {
                    //若無預定行程資料
                    let form = document.querySelector("form");
                    form.style.display = "none";
                    let no_schedule = document.querySelector("div.no_schedule");
                    no_schedule.style.display = "block";
                    let div_n0 = document.querySelector("div.n0");
                    div_n0.innerText = `您好，${res_json.data.user.name}，待預定的行程如下：`;
                }
            });
        }
    });
});
