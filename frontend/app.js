let items = [];
const resultDiv = document.getElementById("result");
const spinBtn = document.getElementById("spin-btn");
const slider = document.getElementById("items-slider");
const BACKEND_API = window.BACKEND_API || "http://localhost:8000";
const tg = window.Telegram?.WebApp;

if (!tg) {
    alert("Ошибка: Telegram WebApp не найден.");
    throw new Error("Telegram WebApp не найден");
}

tg.ready(); // обязательно!

// Отправка initData на сервер для получения chat_id
let chat_id = null;

fetch(`${BACKEND_API}/auth`, {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        init_data: tg.initData // именно tg.initData, не initDataUnsafe!
    })
})
    .then(res => {
        if (!res.ok) throw new Error("Сервер не вернул OK");
        return res.json();
    })
    .then(data => {
        if (!data.chat_id) throw new Error("Сервер не вернул chat_id");
        chat_id = data.chat_id;
        console.log("Получен chat_id с сервера:", chat_id);
        // можно запускать fetchItems или активировать кнопку только после этого
    })
    .catch(err => {
        console.error("Ошибка при получении chat_id:", err);
        alert("Ошибка при получении chat_id: " + err.message);
    });

async function fetchItems() {
    const loader = document.getElementById("loader");
    const spinBtn = document.getElementById("spin-btn");
    const sliderContainer = document.querySelector(".slider-container");

    // Показать главный лоадер
    loader.style.display = "block";
    slider.innerHTML = "";
    sliderContainer.style.display = "none";
    spinBtn.style.display = "none";

    items = await (await fetch(`${BACKEND_API}/items`)).json();

    const imagePromises = [];

    items.forEach(item => {
        const div = document.createElement("div");
        div.className = "item";

        const img = new Image();
        img.src = item.photo_url;
        imagePromises.push(new Promise(resolve => {
            img.onload = resolve;
            img.onerror = resolve;
        }));

        div.innerHTML = `
        <div class="image-container">
          <img src="${item.photo_url}" alt="${item.name}" />
        </div>
        <div class="item-name">${item.name.toUpperCase()}</div>
        <div class="item-probability">Вероятность получения — ${(item.probability * 100).toFixed(1)}%</div>
      `;

        slider.appendChild(div);
    });

    await Promise.all(imagePromises);

    // Прячем главный лоадер, показываем слайдер
    loader.style.display = "none";
    sliderContainer.style.display = "block";
    spinBtn.style.display = "block";

    // Показываем лоадер внутри кнопки на 5 сек
    const originalBtnContent = spinBtn.innerHTML;
    spinBtn.disabled = true;
    spinBtn.innerHTML = `<span class="btn-loader"></span> Загрузка...`;

    await new Promise(resolve => setTimeout(resolve, 5000));

    spinBtn.innerHTML = originalBtnContent;
    spinBtn.disabled = false;

}

function getRandomItem() {
    const rand = Math.random();
    let sum = 0;
    for (const item of items) {
        sum += item.probability;
        if (rand <= sum) return item;
    }
    return items[items.length - 1];
}

let isSpinning = false;

async function spin() {
    if (isSpinning) return;
    isSpinning = true;

    spinBtn.disabled = true;
    spinBtn.classList.add("disabled");

    try {
        const resp = await fetch(`${BACKEND_API}/spin`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ chat_id }),
        });
        if (!resp.ok) throw new Error(`Ошибка сервера: ${resp.status}`);

        const data = await resp.json();

        // Найти предмет в items по item_id из backend
        const selectedItem = items.find(i => i.id === data.item_id);
        if (!selectedItem) throw new Error("Приз не найден");

        // Здесь запускаем анимацию прокрутки, как у тебя было, с selectedItem и index
        // Копируем твою анимацию:
        const index = items.findIndex(i => i.id === selectedItem.id);

        const itemElements = slider.querySelectorAll(".item");
        const itemWidth = itemElements[0].offsetWidth +
            parseInt(getComputedStyle(itemElements[0]).marginLeft) +
            parseInt(getComputedStyle(itemElements[0]).marginRight);

        const containerWidth = slider.parentElement.offsetWidth;
        const centerX = containerWidth / 2;

        const loopCount = 20;
        slider.innerHTML = "";
        for (let i = 0; i < loopCount; i++) {
            items.forEach(item => {
                const div = document.createElement("div");
                div.className = "item";
                div.innerHTML = `
                    <div class="image-container">
                        <img src="${item.photo_url}" alt="${item.name}" />
                    </div>
                    <div class="item-name">${item.name.toUpperCase()}</div>
                    <div class="item-probability">Вероятность получения — ${(item.probability * 100).toFixed(1)}%</div>
                `;
                slider.appendChild(div);
            });
        }

        const finalIndex = items.length * (loopCount - 1) + index;
        const offset = finalIndex * itemWidth - centerX + itemWidth / 2;

        const allItemElements = slider.querySelectorAll(".item");
        allItemElements.forEach(el => el.classList.remove("selected", "dimmed"));

        slider.style.transition = "none";
        slider.style.transform = `translateX(0)`;

        requestAnimationFrame(() => {
            slider.style.transition = "transform 5s cubic-bezier(0.25, 0.1, 0.25, 1)";
            slider.style.transform = `translateX(-${offset}px)`;
        });

        slider.addEventListener("transitionend", async function handler() {
            slider.removeEventListener("transitionend", handler);

            allItemElements.forEach((el, i) => {
                if (i === finalIndex) {
                    el.classList.add("selected");
                } else {
                    el.classList.add("dimmed");
                }
            });

            await new Promise(resolve => setTimeout(resolve, 2000));

            showResult(selectedItem);
            isSpinning = false;
        });
    } catch (e) {
        alert("Ошибка: " + e.message);
        isSpinning = false;
        spinBtn.disabled = false;
        spinBtn.classList.remove("disabled");
    }
}

function showResult(item) {
    // Скрываем слайдер
    document.querySelector(".slider-container").classList.add("hidden");
    document.querySelector("#spin-btn").classList.add("hidden");
    document.querySelector(".under-slider__link").classList.add("hidden");

    // Меняем заголовок
    const title = document.querySelector(".title");
    title.textContent = "ВАШ ПРИЗ!";

    // Добавим текст под заголовком
    const subtitle = document.createElement("p");
    subtitle.textContent = "Уже добавили выигрыш в вашу корзину! Чтобы его разблокировать, введите свою почту. На неё придёт промокод и инструкция";
    subtitle.style.margin = "10px 0";
    subtitle.style.fontSize = "12px";
    title.insertAdjacentElement("afterend", subtitle);

    // Отображаем только выбранный элемент + email форма
    resultDiv.innerHTML = `
      <div class="item selected result">
        <div class="image-container">
          <img src="${item.photo_url}" alt="${item.name}" />
        </div>
        <div class="item-name">${item.name.toUpperCase()}</div>
        <p class="item-probability">Вероятность получения — ${(item.probability * 100).toFixed(1)}%</p>
      </div>
      <form id="email-form">
        <input class="email-input" type="email" id="email" placeholder="E-mail" required />
        <button type="submit" class="get-promo">Прислать промокод</button>
      </form>
      <div id="email-message"></div>
    `;

    // Обработчик формы
    document.getElementById("email-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("email").value;

        try {
            const resp = await fetch(`${BACKEND_API}/claim`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ chat_id, email }),
            });
            if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.detail || "Ошибка при отправке промокода");
            }
            const data = await resp.json();

            document.getElementById("email-message").innerHTML =
                `<p>Промокод будет выслан на <strong>${email}</strong></p>`;
            document.getElementById("email-form").remove();
        } catch (e) {
            document.getElementById("email-message").innerHTML =
                `<p style="color:red;">Ошибка: ${e.message}</p>`;
        }
    });
}

spinBtn.addEventListener("click", spin);
fetchItems();
