// document.addEventListener('DOMContentLoaded', function() {
//     document.body.addEventListener('htmx:oobAfterSwap', function(event) {
//         const block2 = document.getElementById('guessLog');
//         block2.scrollTop = block2.scrollHeight;
//     });
// });

// document.addEventListener('DOMContentLoaded', function() {
//     document.body.addEventListener('htmx:afterOnLoad', function(event) {
//         if (event.detail.elt.getAttribute('hx-swap-oob') !== null) {
//             const block2 = document.getElementById('guessLog');
//             if (block2) {
//                 block2.scrollTop = block2.scrollHeight;
//             }
//         }
//     });
// });

// document.addEventListener('DOMContentLoaded', function() {
//         if (event.detail.elt.getAttribute('hx-swap-oob') !== null) {
//             const block2 = document.getElementById('guessLog');
//             if (block2) {
//                 block2.scrollTop = block2.scrollHeight;
//             }
//         }
// });

// function patchInput() {
//     var inp = document.getElementById("prompt");
//     inp.value += " - Patched String"; // Modify the value by appending a string
// }