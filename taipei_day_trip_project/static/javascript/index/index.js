let div_p1 = document.querySelector("div.p1");
let delay = false; // sovle internet delay problem
let loading_gif = document.querySelector("div.loading");

//create fetch api function :/api/attractions
let page = 0;
let keyword = "";

async function load_trip(pg, kw) {
    if (pg === null) {
        delay = false;
        return;
    }
    loading_gif.style.display = "block";
    let res = await fetch(`/api/attractions?page=${pg}&keyword=${kw}`);
    let res_json = await res.json();
    let load_id = [];
    let load_image = [];
    let load_name = [];
    let load_mrt = [];
    let load_category = [];
    if (res_json.error) {
        let div_p2 = document.createElement("div");
        div_p2.classList.add("p2");
        div_p2.innerText = res_json.message;
        div_p1.appendChild(div_p2);
        page = null;
        delay = false;
    } else {
        item_num = res_json.data.length;
        for (let i = 0; i < item_num; i++) {
            load_id.push(res_json.data[i].id);
            load_image.push(res_json.data[i].images[0]);
            load_name.push(res_json.data[i].name);
            load_category.push(res_json.data[i].category);
            load_mrt.push(res_json.data[i].mrt);
        }
        // generate_pic(item_num);
        for (let i = 0; i < item_num; i++) {
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
            delay = false;
            div_p2.addEventListener("click", (e) => {
                location.href = `/attraction/${load_id[i]}`;
            });
        }
        page = res_json.nextPage;
    }
    if (window.innerHeight == document.documentElement.scrollHeight) {
        load_trip(page, keyword);
    }
    loading_gif.style.display = "none";
}

/////////////////////////////////////////////
//////// window load EVENT //////////////////
/////////////////////////////////////////////
window.addEventListener("load", (e) => {
    load_trip(page, keyword);
});

/////////////////////////////////////////////
/////////////// infinite scroll EVENT ///////
/////////////////////////////////////////////

window.addEventListener("scroll", (e) => {
    if (
        window.scrollY + window.innerHeight >=
        document.documentElement.scrollHeight - 135
    ) {
        if (!delay) {
            console.log(document.documentElement.scrollHeight);
            delay = true;
            load_trip(page, keyword);
        }
    }
});

/////////////////////////////////////////////
/////////////// keyword searching ///////////
/////////////////////////////////////////////
let input = document.querySelector("input");
let button = document.querySelector("button");

button.addEventListener("click", (e) => {
    console.log("ccc");
    if (!delay) {
        page = 0;
        keyword = input.value;
        let all_div_p2 = document.querySelectorAll("div.p2");
        all_div_p2.forEach((div_p2) => {
            div_p2.remove();
        });
        delay = true;
        load_trip(page, keyword);
    }
});

input.addEventListener("keyup", (e) => {
    if (e.code === "Enter") {
        button.click();
    }
});

// //以下測試中以下測試中以下測試中以下測試中以下測試中以下測試中以下測試中以下測試中以下測試中以下測試中以下測試中以下測試中以下測試中
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
