let items = [];
const resultDiv = document.getElementById("result");
const spinBtn = document.getElementById("spin-btn");
const slider = document.getElementById("items-slider");
const BACKEND_API = window.BACKEND_API || "http://localhost:8000";

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

function spin() {
    if (isSpinning) return;
    isSpinning = true;

    const selectedItem = getRandomItem();
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
        // Делаем длительность 5 секунд и easing плавное ease-out
        slider.style.transition = "transform 5s cubic-bezier(0.25, 0.1, 0.25, 1)";
        slider.style.transform = `translateX(-${offset}px)`;
    });

    slider.addEventListener("transitionend", function handler() {
        slider.removeEventListener("transitionend", handler);

        allItemElements.forEach((el, i) => {
            if (i === finalIndex) {
                el.classList.add("selected");
            } else {
                el.classList.add("dimmed");
            }
        });

        showResult(selectedItem);
        isSpinning = false;
    });
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

        await fetch(`${BACKEND_API}/claim`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, item_id: item.id }),
        });

        document.getElementById("email-message").innerHTML = `<p>Промокод будет выслан на <strong>${email}</strong></p>`;
        document.getElementById("email-form").remove();
    });
}

spinBtn.addEventListener("click", spin);
fetchItems();
