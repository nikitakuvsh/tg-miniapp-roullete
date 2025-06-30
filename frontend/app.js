let items = [];
const resultDiv = document.getElementById("result");
const spinBtn = document.getElementById("spin-btn");
const slider = document.getElementById("items-slider");
const BACKEND_API = window.BACKEND_API || "http://localhost:8000";

let tg = window.Telegram.WebApp;
tg.ready();
let userId = null;

try {
    userId = tg.initDataUnsafe.user.id;
} catch (e) {
    console.log('fail', e);
}

function showResultById(item_id) {
    const item = items.find(i => i.id === item_id);
    if (item) {
        showResult(item);
    } else {
        console.error("Не найден предмет с id", item_id);
    }
}


checkSpin();

async function checkSpin() {
    const resp = await fetch(`${BACKEND_API}/has_spun?chat_id=${userId}`);
    const data = await resp.json();

    if (data.already_spun) {
        showResultById(data.item_id);
    } else {
        fetchItems();
    }
}

function shortenName(name) {
    if (name.length > 15) {
        return name.slice(0, 12) + '...';
    }
    return name;
}

async function fetchItems() {
    const loader = document.getElementById("loader");
    const sliderContainer = document.querySelector(".slider-container");

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
        <div class="item-name">${shortenName(item.name).toUpperCase()}</div>
        <div class="item-probability">Вероятность получения — ${(item.probability * 100).toFixed(1)}%</div>
      `;

        slider.appendChild(div);
    });

    await Promise.all(imagePromises);

    loader.style.display = "none";
    sliderContainer.style.display = "block";
    spinBtn.style.display = "block";

    const originalBtnContent = spinBtn.innerHTML;
    spinBtn.disabled = true;
    spinBtn.innerHTML = `<span class="btn-loader"></span> Загрузка...`;

    await new Promise(resolve => setTimeout(resolve, 5000));

    spinBtn.innerHTML = originalBtnContent;
    spinBtn.disabled = false;
}


let isSpinning = false;

async function spin() {
    if (isSpinning) return;
    isSpinning = true;

    spinBtn.disabled = true;
    spinBtn.classList.add("disabled");

    try {
        // Получаем результат спина с сервера
        const resp = await fetch(`${BACKEND_API}/spin`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ chat_id: userId }),
        });
        if (!resp.ok) throw new Error(`Ошибка сервера: ${resp.status}`);

        const data = await resp.json();

        // Фильтруем доступные призы с quantity > 0
        const availableItems = items.filter(i => i.quantity > 0);

        // Ищем выбранный предмет в доступных призах
        let selectedItem = availableItems.find(i => i.id === data.item_id);

        // Если вдруг не нашли, для безопасности — берём первый доступный предмет
        if (!selectedItem) selectedItem = availableItems[0];

        // Индекс выбранного предмета в списке доступных призов
        const index = availableItems.findIndex(i => i.id === selectedItem.id);

        // Подготовка слайдера с доступными призами
        const loopCount = 20;
        slider.innerHTML = "";
        for (let i = 0; i < loopCount; i++) {
            availableItems.forEach(item => {
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

        // Ждем, пока все изображения загрузятся, чтобы корректно измерить размеры
        const imgs = slider.querySelectorAll("img");
        await Promise.all(Array.from(imgs).map(img => {
            return new Promise(resolve => {
                if (img.complete) {
                    resolve();
                } else {
                    img.onload = resolve;
                    img.onerror = resolve;
                }
            });
        }));

        const itemElements = slider.querySelectorAll(".item");
        if (itemElements.length === 0) throw new Error("Нет элементов для показа");

        // Размер одного элемента с учётом margin
        const style = getComputedStyle(itemElements[0]);
        const itemWidth = itemElements[0].offsetWidth +
            parseFloat(style.marginLeft) +
            parseFloat(style.marginRight);

        const containerWidth = slider.parentElement.offsetWidth;
        const centerX = containerWidth / 2;

        // Вычисляем финальный индекс прокрутки с учётом количества циклов
        const finalIndex = availableItems.length * (loopCount - 1) + index;

        // Смещение для центрирования выбранного предмета
        const offset = finalIndex * itemWidth - centerX + itemWidth / 2;

        // Убираем выделения и затемняем все
        itemElements.forEach(el => el.classList.remove("selected", "dimmed"));

        // Сброс трансформации для корректного старта
        slider.style.transition = "none";
        slider.style.transform = `translateX(0)`;

        // Даем браузеру прогрузить стиль перед анимацией
        await new Promise(r => requestAnimationFrame(r));

        // Небольшая задержка для мобильных браузеров (устранение сбоев с расчетом)
        await new Promise(r => setTimeout(r, 50));

        // Запускаем анимацию прокрутки
        slider.style.transition = "transform 5s cubic-bezier(0.25, 0.1, 0.25, 1)";
        slider.style.transform = `translateX(-${offset}px)`;

        // Обработчик окончания анимации
        slider.addEventListener("transitionend", async function handler() {
            slider.removeEventListener("transitionend", handler);

            itemElements.forEach((el, i) => {
                if (i === finalIndex) {
                    el.classList.add("selected");
                } else {
                    el.classList.add("dimmed");
                }
            });

            // Пауза перед показом результата
            await new Promise(resolve => setTimeout(resolve, 2000));

            showResult(selectedItem);

            isSpinning = false;
            spinBtn.disabled = false;
            spinBtn.classList.remove("disabled");
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
                body: JSON.stringify({ chat_id: userId, email }),
            });
            if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.detail || "Ошибка при отправке промокода");
            }
            const data = await resp.json();

            document.getElementById("email-message").innerHTML =
                `<p style="margin-top: 5px">Промокод успешно выслан на <strong>${email}</strong></p>`;
            document.getElementById("email-form").remove();
        } catch (e) {
            document.getElementById("email-message").innerHTML =
                `<p style="color:red;">Ошибка: ${e.message}</p>`;
        }
    });
}

spinBtn.addEventListener("click", spin);
