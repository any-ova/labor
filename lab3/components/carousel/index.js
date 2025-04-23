export function Carousel(items) {
    return `
        <div id="carouselExample" class="carousel slide" data-bs-ride="carousel">
            <div class="carousel-inner">
                ${items.map((item, index) => `
                    <div class="carousel-item ${index === 0 ? 'active' : ''}">
                        <img src="${item.image}" class="d-block w-100" style="height: 300px; object-fit: contain;" alt="${item.alt}">
                    </div>
                `).join('')}
            </div>
            <button class="carousel-control-prev" type="button" data-bs-target="#carouselExample" data-bs-slide="prev">
                <span class="carousel-control-prev-icon" style="background-color: #0c6eff; border-radius: 50%; width: 40px; height: 40px;"></span>
                <span class="visually-hidden">Previous</span>
            </button>
            <button class="carousel-control-next" type="button" data-bs-target="#carouselExample" data-bs-slide="next">
                <span class="carousel-control-next-icon" style="background-color: #0c6eff; border-radius: 50%; width: 40px; height: 40px;"></span>
                <span class="visually-hidden">Next</span>
            </button>
        </div>
        
        <style>
            .carousel-control-prev-icon,
            .carousel-control-next-icon {
                background-color: #0c6eff; 
                border-radius: 50%;
                width: 40px;
                height: 40px;
                background-size: 50% 50%; /* Размер стрелки внутри круга */
                opacity: 0.8;
                transition: opacity 0.3s;
            }
            
            .carousel-control-prev-icon:hover,
            .carousel-control-next-icon:hover {
                opacity: 1;
            }
            
            .carousel-control-prev {
                left: 15px;
            }
            
            .carousel-control-next {
                right: 15px;
            }
        </style>
    `;
}