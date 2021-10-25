/**
 * @param {any} value
 * @returns {boolean}
 */
function not(value) {
    return !value;
}

module.exports = Object.defineProperties(not, {
    default: { value: not },
    not: { value: not },
    __esModule: { value: true },
});
