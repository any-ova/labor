export function ProductCard({ title, description, onClick, color, image }) {
    return `
        <div class="col-md-4">
            <div class="card h-100">
                <img src="${image}" class="card-img-top" alt="${title}" style="height: 180px; object-fit: cover;">
                <div class="card-body">
                    <h5 class="card-title">${title}</h5>
                    <p class="card-text">${description}</p>
                    <button class="btn ${color} text-white" onclick="${onClick}">Перейти</button>
                </div>
            </div>
        </div>
    `;
}