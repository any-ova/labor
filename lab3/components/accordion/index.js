export function Accordion(items) {
    return `
        <div class="accordion" id="accordionExample">
            ${items.map((item, index) => `
                <div class="accordion-item">
                    <h2 class="accordion-header" id="heading${index}">
                        <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${index}" aria-expanded="${index === 0 ? 'true' : 'false'}" aria-controls="collapse${index}">
                            ${item.title}
                        </button>
                    </h2>
                    <div id="collapse${index}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}" aria-labelledby="heading${index}" data-bs-parent="#accordionExample">
                        <div class="accordion-body">
                            ${item.content}
                            <img src="${item.gif}" class="img-fluid mt-2" style="height: 200px; object-fit: cover;">
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}
