export class BackButtonComponent {
    constructor(parent) {
        this.parent = parent;
    }

    getHTML() {
        return `
            <button class="back-button">
                <span><i class="bi bi-arrow-left"></i> Back</span>
            </button>
        `;
    }

    render(listener) {
        if (this.parent) {
            const html = this.getHTML();
            this.parent.insertAdjacentHTML('beforeend', html);
            this.parent.querySelector('.back-button').addEventListener('click', listener);
        }
    }
}