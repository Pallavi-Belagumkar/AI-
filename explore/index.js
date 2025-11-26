// 🌿 Krishsiri Frontend Script - Connected to Flask Backend
// ---------------------------------------------------------

const BACKEND_URL = "http://127.0.0.1:5000"; // 🔗 Flask server base URL

// ✅ Responsive Navigation
const menuBtn = document.createElement("button");
menuBtn.classList.add("mobile-menu-btn");
menuBtn.innerHTML = `<i class="fas fa-bars"></i>`;
document.querySelector(".nav-container").appendChild(menuBtn);

menuBtn.addEventListener("click", () => {
  const navLinks = document.querySelector(".nav-links");
  navLinks.classList.toggle("active");
  menuBtn.querySelector("i").classList.toggle("fa-times");
});

// ✅ Smooth Scroll
document.querySelectorAll('nav a[href^="#"]').forEach(anchor => {
  anchor.addEventListener("click", e => {
    e.preventDefault();
    const target = document.querySelector(anchor.getAttribute("href"));
    if (target) target.scrollIntoView({ behavior: "smooth" });
  });
});

// ✅ FAQ Toggle
document.querySelectorAll(".faq-question").forEach(question => {
  question.addEventListener("click", () => {
    const answer = question.nextElementSibling;
    answer.classList.toggle("active");
    const icon = question.querySelector("i");
    icon.classList.toggle("fa-chevron-up");
    icon.classList.toggle("fa-chevron-down");
  });
});

// ✅ Crop Recommendation (connects to Flask /predict_crop)
const cropForm = document.getElementById("cropForm");
if (cropForm) {
  cropForm.addEventListener("submit", async e => {
    e.preventDefault();
    const cropType = document.getElementById("cropType").value;
    const soil = document.getElementById("soilType").value;
    const rainfall = document.getElementById("rainfall").value;
    const resultBox = document.getElementById("cropResult");

    if (!cropType || !soil || !rainfall) {
      resultBox.textContent = "⚠️ Please fill in all fields.";
      resultBox.style.display = "block";
      return;
    }

    resultBox.textContent = "🌱 Processing your crop recommendation...";
    resultBox.style.display = "block";

    try {
      const response = await fetch(`${BACKEND_URL}/predict_crop`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          crop_type: cropType,
          soil_type: soil,
          rainfall: rainfall
        })
      });

      const data = await response.json();
      resultBox.textContent = `✅ Recommended Crop: ${data.recommended_crop}`;
    } catch (error) {
      console.error(error);
      resultBox.textContent = "❌ Error: Unable to connect to server.";
    }
  });
}

// ✅ Disease Detection (connects to Flask /detect_disease)
const diseaseForm = document.getElementById("diseaseForm");
if (diseaseForm) {
  diseaseForm.addEventListener("submit", async e => {
    e.preventDefault();
    const fileInput = document.getElementById("plantImage");
    const diseaseResult = document.getElementById("diseaseResult");

    if (fileInput.files.length === 0) {
      diseaseResult.textContent = "⚠️ Please upload an image.";
      diseaseResult.style.display = "block";
      return;
    }

    const formData = new FormData();
    formData.append("image", fileInput.files[0]);

    diseaseResult.textContent = "🔍 Analyzing image, please wait...";
    diseaseResult.style.display = "block";

    try {
      const response = await fetch(`${BACKEND_URL}/detect_disease`, {
        method: "POST",
        body: formData
      });

      const data = await response.json();
      diseaseResult.textContent = `🩺 Result: ${data.disease_result}`;
    } catch (error) {
      console.error(error);
      diseaseResult.textContent = "❌ Error: Unable to connect to server.";
    }
  });
}

// ✅ Language Toggle (English <-> Kannada)
const langBtn = document.createElement("button");
langBtn.textContent = "🌐 ಕನ್ನಡ / English";
langBtn.classList.add("lang-toggle");
document.querySelector(".nav-container").appendChild(langBtn);

let isKannada = false;
langBtn.addEventListener("click", () => {
  isKannada = !isKannada;
  translatePage(isKannada);
});

const translations = {
  kn: {
    "Crop Recommendation": "ಬೆಳೆ ಶಿಫಾರಸು",
    "Disease Detection": "ರೋಗ ಪತ್ತೆ",
    "Weather & Price": "ಹವಾಮಾನ ಮತ್ತು ಬೆಲೆ",
    "About": "ನಮ್ಮ ಬಗ್ಗೆ",
    "Contact": "ಸಂಪರ್ಕಿಸಿ",
    "Smart Farming Assistant": "ಸ್ಮಾರ್ಟ್ ಕೃಷಿ ಸಹಾಯಕ",
    "Predict Best Crop": "ಉತ್ತಮ ಬೆಳೆ ಊಹಿಸಿ",
    "Upload Leaf Image": "ಎಲೆ ಚಿತ್ರವನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ"
  }
};

function translatePage(toKannada) {
  document.querySelectorAll("nav a, h1, h2, h3, button, label, .feature-card h3")
    .forEach(el => {
      const text = el.textContent.trim();
      if (toKannada && translations.kn[text]) el.textContent = translations.kn[text];
      else {
        const original = Object.entries(translations.kn).find(([en, kn]) => kn === text);
        if (original) el.textContent = original[0];
      }
    });
}

// ✅ Scroll Animation
window.addEventListener("scroll", () => {
  document.querySelectorAll(".feature-card, section").forEach(el => {
    const position = el.getBoundingClientRect().top;
    const windowHeight = window.innerHeight;
    if (position < windowHeight - 100) el.classList.add("visible");
  });
});
