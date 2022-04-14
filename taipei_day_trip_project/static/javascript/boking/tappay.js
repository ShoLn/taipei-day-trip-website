// Tappay SDK
TPDirect.setupSDK(
    123962,
    "app_5DTa4IpzxR86YBHcXayVr0WPQNcdm4AepI52Xw4K5KyOEWpceg3mv85G3TRG",
    "sandbox"
);

var fields = {
    number: {
        // css selector
        element: "#card-number",
        placeholder: "**** **** **** ****",
    },
    expirationDate: {
        // DOM object
        element: document.getElementById("card-expiration-date"),
        placeholder: "MM / YY",
    },
    ccv: {
        element: "#card-ccv",
        placeholder: "後三碼",
    },
};

// css style
TPDirect.card.setup({
    fields: fields,
    styles: {
        // Style all elements
        input: {
            color: "black",
        },
        // Styling ccv field
        "input.ccv": {
            "font-size": "16px",
        },
        // Styling expiration-date field
        "input.expiration-date": {
            "font-size": "16px",
        },
        // Styling card-number field
        "input.card-number": {
            "font-size": "16px",
        },
        // style focus state
        ":focus": {
            color: "black",
        },
        // style valid state
        ".valid": {
            color: "#448899",
        },
        // style invalid state
        ".invalid": {
            color: "#a41d1d",
        },
    },
});

// 監測輸入欄狀況已做出相對應css 跟 button可否按下功能
TPDirect.card.onUpdate(function (update) {
    // update.canGetPrime === true
    // --> you can call TPDirect.card.getPrime()
    if (update.canGetPrime) {
        // Enable submit Button to get prime.
        document.querySelector("button.tapfield").removeAttribute("disabled");
    } else {
        // Disable submit Button to get prime.
        document
            .querySelector("button.tapfield")
            .setAttribute("disabled", true);
    }
    /* Change card type display when card type change */
    /* ============================================== */

    // cardTypes = ['visa', 'mastercard', ...]
    let newType = update.cardType === "unknown" ? "" : update.cardType;
    let number_span = document.querySelector(".number");
    let expiry_span = document.querySelector(".expiry");
    let ccv_span = document.querySelector(".ccv");
    // number 欄位是錯誤的
    if (update.status.number === 2) {
        number_span.innerText = "資料有誤請檢查";
        number_span.style.color = "#a41d1d";
    } else if (update.status.number === 0) {
        number_span.innerText = newType;
        number_span.style.color = "#448899";
    } else {
        number_span.innerText = "";
    }

    if (update.status.expiry === 2) {
        expiry_span.innerText = "資料有誤請檢查";
        expiry_span.style.color = "#a41d1d";
    } else if (update.status.expiry === 0) {
        expiry_span.innerText = "資料格式正確";
        expiry_span.style.color = "#448899";
    } else {
        expiry_span.innerText = "";
    }

    if (update.status.ccv === 2) {
        ccv_span.innerText = "資料有誤請檢查";
        ccv_span.style.color = "#a41d1d";
    } else if (update.status.ccv === 0) {
        ccv_span.innerText = "資料格式正確";
        ccv_span.style.color = "#448899";
    } else {
        ccv_span.innerText = "";
    }
});

// 取得預定行程資料api function
async function api_booking(method) {
    let res = await fetch("/api/booking", {
        method: method,
        headers: {
            "Content-Type": "application/json",
        },
    });
    res_json = await res.json();
    return res_json;
}

// 訂單編號 api_function
async function api_orders(method, data) {
    let res = await fetch("/api/orders", {
        method: method,
        headers: {
            "Content-Type": "application/json",
        },
        body: data,
    });
    let res_json = await res.json();
    return res_json;
}

// 取得prime
let form_tappay = document.querySelector("form");
form_tappay.addEventListener("submit", (e) => {
    e.preventDefault();
    // 取得 TapPay Fields 的 status
    const tappayStatus = TPDirect.card.getTappayFieldsStatus();

    // 確認是否可以 getPrime
    if (tappayStatus.canGetPrime === false) {
        alert("can not get prime");
        return;
    }

    // Get prime
    TPDirect.card.getPrime((res_prime) => {
        let res_booking = api_booking("GET");
        res_booking.then((booking_data) => {
            let all_booking_id = [];
            booking_data.data.attrac.forEach((att_obj) => {
                all_booking_id.push(att_obj.booking_id);
            });
            all_booking_id = all_booking_id.toString();
            let contact_name = document.querySelector(
                "div.u2 input[id='name']"
            ).value;
            let contact_email = document.querySelector(
                "div.u2 input[id='email']"
            ).value;
            let contact_phone = document.querySelector(
                "div.u2 input[id='phone']"
            ).value;
            let total_price = Number(
                document.querySelector("div.confirm1").innerText.split(" ")[1]
            );
            request_data = JSON.stringify({
                prime: res_prime.card.prime,
                user: {
                    user_id: booking_data.data.user.id,
                    contact_name: contact_name,
                    contact_email: contact_email,
                    contact_phone: contact_phone,
                },
                order: {
                    all_booking_id: all_booking_id,
                    total_price: total_price,
                },
            });
            let res_orders = api_orders("POST", request_data);
            res_orders.then((res_orders_json) => {
                if (!res_orders_json.error) {
                    location.href = `/thankyou?number=${res_orders_json.data.number}`;
                } else {
                    alert(res_orders_json.message);
                }
            });
        });
    });
});
