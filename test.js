let a = document.querySelector(".a");
let b = document.querySelector(".b");
let bu = document.querySelector("div.a button");

a.addEventListener("click", (e) => {
    console.log("a");
});

b.addEventListener("click", (e) => {
    console.log("b");
});

bu.addEventListener("click", (e) => {
    console.log("bu");
});
