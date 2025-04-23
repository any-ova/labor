import { ProductCard } from '../../components/product-card/index.js';

export function renderMainPage() {
    const cards = [
        {
            title: 'Коты',
            description: 'Смешные и милые котики в GIF.',
            onClick: 'renderCatsPage()',
            color: 'bg-primary',
            image: 'img/cats-preview.jpg'

        },
        {
            title: 'Путешествия',
            description: 'Советы для вашего следующего приключения.',
            onClick: 'renderTravelPage()',
            color: 'bg-primary',
            image: 'img/travel-preview.jpg'
        },
        {
            title: 'Искусство',
            description: 'Посмотрите на известные картины.',
            onClick: 'renderArtPage()',
            color: 'bg-primary',
            image: 'img/art-preview.jpg'
        }
    ];

    document.getElementById('app').innerHTML = `
        <div class="container">
            <h1 class="text-primary mb-4">Добро пожаловать на видеохостинг!</h1>
            <div class="row g-4">
                ${cards.map(card => ProductCard(card)).join('')}
            </div>
        </div>
    `;
}