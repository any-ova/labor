import { Accordion } from '../../components/accordion/index.js';

export function renderTravelPage() {
    const travelTips = [
        {
            title: 'Совет 1',
            content: 'Планируйте свой маршрут заранее.',
            gif: 'img/travel1.gif'
        },
        {
            title: 'Совет 2',
            content: 'Убедитесь, что у вас есть страховка.',
            gif: 'img/travel2.gif'
        },
        {
            title: 'Совет 3',
            content: 'Не забудьте о местной культуре.',
            gif: 'img/travel3.gif'
        }
    ];

    document.getElementById('app').innerHTML = `
        <div class="container mt-5">
            <h2>Путешествия</h2>
            ${Accordion(travelTips)}
            <button class="btn btn-secondary mt-3" onclick="renderMainPage()">Назад на главную</button>
        </div>
    `;
}
