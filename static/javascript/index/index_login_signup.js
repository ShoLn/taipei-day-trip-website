let login_signup = document.querySelectorAll("div.nav5")[1]; //最上方 登入/註冊 div
// 登入頁面
let pop_login = document.querySelector(".pop_outest"); //登入視窗
let login_close = document.querySelector("div.pop0 img"); // 登入視窗關閉鈕
let no_account = document.querySelector("div.pop1"); //還沒有帳戶點此註冊鈕
let login_email = pop_login.querySelector("input[name='email']"); //登入信箱
let login_password = pop_login.querySelector("input[name='password']"); //登入密碼
let login = pop_login.querySelector("button"); //登入按鈕
//註冊頁面
let pop_signup = document.querySelectorAll(".pop_outest")[1]; // 註冊視窗
let signup_close = document.querySelectorAll("div.pop0 img")[1]; // 註冊視窗關閉鈕
let have_account = document.querySelectorAll("div.pop1")[1]; //已經有帳戶了點此登入鈕
let signup_name = pop_signup.querySelector("input[name='name']"); //註冊名稱
let signup_email = pop_signup.querySelector("input[name='email']"); //註冊信箱
let signup_password = pop_signup.querySelector("input[name='password']"); // 註冊密碼
let signup = pop_signup.querySelector("button"); // 註冊按鈕

// 每次載入頁時面使用get /api/user 判斷是否已經登入 及 delete /api/suer製作登出按鈕
window.addEventListener("load", (e) => {
    //determine login
    let res_login = api_user("GET", null);
    res_login.then((res_json) => {
        if (res_json.null) {
            return;
        } else {
            let login_signup = document.querySelectorAll("div.nav5")[1];
            login_signup.style.display = "none";
            let signout = document.createElement("div");
            signout.innerText = "登出系統";
            signout.classList.add("signout");
            let div_nav4 = document.querySelector("div.nav4");
            div_nav4.appendChild(signout);
            // signout click event useing delete api
            signout.addEventListener("click", (e) => {
                let res_logout = api_user("DELETE", null);
                res_logout.then((res_json) => {
                    if (res_json.ok) {
                        location.href = window.location.href;
                    }
                });
            });
        }
    });
});

//清除之前登入失敗或成功訊息的function

function delete_message(pop) {
    let div_error = pop.querySelector("div.error");
    let div_success = pop.querySelector("div.success");
    if (div_error) {
        div_error.remove();
    } else if (div_success) {
        div_success.remove();
    }
}

login_signup.addEventListener("click", (e) => {
    pop_login.style.display = "flex";
});

login_close.addEventListener("click", (e) => {
    delete_message(pop_login);
    pop_login.style.display = "none";
});

no_account.addEventListener("click", (e) => {
    delete_message(pop_login);
    pop_login.style.display = "none";
    pop_signup.style.display = "flex";
});

signup_close.addEventListener("click", (e) => {
    delete_message(pop_signup);
    pop_signup.style.display = "none";
});

have_account.addEventListener("click", (e) => {
    delete_message(pop_signup);
    pop_signup.style.display = "none";
    pop_login.style.display = "flex";
});

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

// 註冊按鈕click事件 api POST
signup.addEventListener("click", (e) => {
    delete_message(pop_signup);
    //檢查是否有欄位是空白格式
    if (
        signup_name.value == "" ||
        signup_email.value == "" ||
        signup_password.value == ""
    ) {
        let error_message = document.createElement("div");
        error_message.classList.add("error");
        error_message.innerText = "不可有任一欄位為空白";
        error_message.style.color = "red";
        signup.after(error_message);
        return;
    }
    //檢查email格式
    let regexEmail = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    if (!signup_email.value.match(regexEmail)) {
        let error_message = document.createElement("div");
        error_message.classList.add("error");
        error_message.innerText = "請輸入有效的email";
        error_message.style.color = "red";
        signup.after(error_message);
        return;
    }

    // POST api
    let data = JSON.stringify({
        name: signup_name.value,
        email: signup_email.value,
        password: signup_password.value,
    });

    let res = api_user("POST", data);
    res.then((res_json) => {
        if (res_json.ok) {
            let success = document.createElement("div");
            success.classList.add("success");
            success.innerText = "註冊成功";
            success.style.color = "green";
            signup.after(success);
        } else {
            let error_message = document.createElement("div");
            error_message.classList.add("error");
            error_message.innerText = res_json.message;
            error_message.style.color = "red";
            signup.after(error_message);
        }
    });
});

//登入按鈕click事件 api PATCH
login.addEventListener("click", (e) => {
    delete_message(pop_login);
    //檢查是否有欄位是空白格式
    if (login_email.value == "" || login_password.value == "") {
        let error_message = document.createElement("div");
        error_message.classList.add("error");
        error_message.innerText = "不可有任一欄位為空白";
        error_message.style.color = "red";
        login.after(error_message);
        return;
    }
    //檢查email格式
    let regexEmail = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    if (!login_email.value.match(regexEmail)) {
        let error_message = document.createElement("div");
        error_message.classList.add("error");
        error_message.innerText = "請輸入有效的email";
        error_message.style.color = "red";
        login.after(error_message);
        return;
    }
    // PATCH api
    let data = JSON.stringify({
        email: login_email.value,
        password: login_password.value,
    });
    let res = api_user("PATCH", data);
    res.then((res_json) => {
        if (res_json.ok) {
            pop_login.style.display = "none";
            location.href = window.location.href;
        } else {
            let error_message = document.createElement("div");
            error_message.classList.add("error");
            error_message.innerText = res_json.message;
            error_message.style.color = "red";
            login.after(error_message);
        }
    });
});
