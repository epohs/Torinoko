


const passphrase_field = document.getElementById('passphrase');
const counter_el = document.querySelector(".field-wrap.field-passphrase .passphrase-char-count .cur-chars");







// Wait until HTML has been parsed
document.addEventListener('DOMContentLoaded', () => {
  

  document.body.classList.remove('no-js');


  // Update the counter on every keystroke
  passphrase_field.addEventListener('keyup', update_passphrase_counter);

  
}); // ( DOMContentLoaded )





function update_passphrase_counter() {

  const characterCount = passphrase_field.value.length;
  counter_el.textContent = characterCount;

}
