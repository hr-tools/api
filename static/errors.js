import {modals, spawnModal} from '/static/modal.js';

export function showError(message) {
    spawnModal(modals.error)
    const errorP = document.getElementById('error-message')
    errorP.innerText = message
}
