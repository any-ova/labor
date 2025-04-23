import { renderMainPage } from './pages/main/index.js';
import { renderCatsPage } from './pages/cats/index.js';
import { renderTravelPage } from './pages/travel/index.js';
import { renderArtPage } from './pages/art/index.js';

document.addEventListener('DOMContentLoaded', () => {
    renderMainPage();
});

// Сделаем функции доступными глобально
window.renderMainPage = renderMainPage;
window.renderCatsPage = renderCatsPage;
window.renderTravelPage = renderTravelPage;
window.renderArtPage = renderArtPage;