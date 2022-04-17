// 取得query string 訂單編號
const params = new Proxy(new URLSearchParams(window.location.search), {
    get: (searchParams, prop) => searchParams.get(prop),
});
let order_id = params.number;
let div_order_id = document.querySelectorAll("div.oc3")[0];
let div_price = document.querySelectorAll("div.oc3")[1];
let div_payment = document.querySelectorAll("div.oc3")[2];

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
window.addEventListener("load", (e) => {
    let res = api_user("GET", null);
    res.then((res_json) => {
        if (res_json.null) {
            location.href = "/";
        } else {
            fetch(`/api/order/${order_id}`)
                .then((res) => {
                    return res.json();
                })
                .then((res_json) => {
                    div_order_id.innerText = res_json.data.number;
                    div_price.innerText = res_json.data.price;
                    if (res_json.data.status == 0) {
                        div_payment.innerText = "已付款";
                    } else {
                        div_payment.innerText = "尚未付款";
                    }
                });
        }
    });
});
