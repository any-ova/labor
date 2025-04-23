export function ButtonGroup(buttons) {
    return `
        <div class="btn-group" role="group" aria-label="Navigation">
            ${buttons.map((btn) => `
                <button type="button" class="btn btn-primary" onclick="${btn.onClick}">${btn.label}</button>
            `).join('')}
        </div>
    `;
}
