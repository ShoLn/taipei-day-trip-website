let div_p1 = document.querySelector("div.p1");

//create generate html pictre function
function generate_pic(number) {
    for (let i = 0; i < number; i++) {
        let div_p2 = document.createElement("div");
        div_p2.classList.add("p2");
        let img = document.createElement("img");
        img.classList.add("pi");
        let div_p3 = document.createElement("div");
        div_p3.classList.add("p3");
        let div_p4 = document.createElement("div");
        div_p4.classList.add("p4");
        let div_p5 = document.createElement("div");
        div_p5.classList.add("p5");
        let div_p6 = document.createElement("div");
        div_p6.classList.add("p6");
        div_p1.appendChild(div_p2);
        div_p2.appendChild(img);
        div_p2.appendChild(div_p3);
        div_p2.appendChild(div_p4);
        div_p4.appendChild(div_p5);
        div_p4.appendChild(div_p6);
        img.src = load_image[i];
        div_p3.innerText = load_name[i];
        div_p5.innerText = load_mrt[i];
        div_p6.innerText = load_category[i];
    }
}

//create fetch api function :/api/attractions
let page = 0;
let keyword = "";
async function load_trip(pg, kw) {
    if (pg === null) {
        return;
    }
    let res = await fetch(`/api/attractions?page=${pg}&keyword=${kw}`);
    let res_json = await res.json();
    load_image = [];
    load_name = [];
    load_mrt = [];
    load_category = [];
    if (res_json.error) {
        let div_p2 = document.createElement("div");
        div_p2.classList.add("p2");
        div_p2.innerText = res_json.message;
        div_p1.appendChild(div_p2);
    } else {
        item_num = res_json.data.length;
        for (let i = 0; i < item_num; i++) {
            load_image.push(res_json.data[i].images[0]);
            load_name.push(res_json.data[i].name);
            load_category.push(res_json.data[i].category);
            load_mrt.push(res_json.data[i].mrt);
        }
        generate_pic(item_num);
        page = res_json.nextPage;
    }
}

// fetch img when window load
window.addEventListener("load", (e) => {
    load_trip(page, keyword);
});

// fetch img when scroll to bottom
window.addEventListener("scroll", (e) => {
    if (
        window.scrollY + window.innerHeight >=
        document.documentElement.scrollHeight - 135
    ) {
        load_trip(page, keyword);
    }
});

// keyword searching
let input = document.querySelector("input");
let button = document.querySelector("button");

button.addEventListener("click", (e) => {
    let page = 0;
    let keyword = input.value;
    let all_div_p2 = document.querySelectorAll("div.p2");
    all_div_p2.forEach((div_p2) => {
        div_p2.remove();
    });
    load_trip(page, keyword);
});

input.addEventListener("keyup", (e) => {
    if (e.code === "Enter") {
        button.click();
    }
});

// //以下測試中
// //intersectionobserver
// let div_obt = document.querySelector("div.obt");
// options = {
//     root: null,
//     threshold: 0,
// };
// let observe_obj = new IntersectionObserver((entries, observe_obj) => {
//     console.log(entries[0].isIntersecting);
//     if (entries[0].isIntersecting) {
//         console.log("observe");
//         load_trip(page, keyword);
//     }
// }, options);
// observe_obj.observe(div_obt);

// // keyword search
// let button = document.querySelector("button");
// button.addEventListener("click", (e) => {
//     page = 0;
//     keyword = document.querySelector("input").value;
//     let all_div_p2 = document.querySelectorAll("div.p2");
//     all_div_p2.forEach((div_p2) => {
//         div_p2.remove();
//     });
// });
