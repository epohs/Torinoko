


const passphrase_field = document.querySelector('.field-wrap.field-passphrase .note-passphrase.has-counter');
const counter_el = document.querySelector('.field-wrap.field-passphrase .passphrase-char-count .cur-chars');







// Wait until HTML has been parsed
document.addEventListener('DOMContentLoaded', () => {
  

  document.body.classList.remove('no-js');


  if ( passphrase_field ) {
  
    // Update the counter on every keystroke
    passphrase_field.addEventListener('keyup', update_passphrase_counter);
    
  }

  
}); // ( DOMContentLoaded )





function update_passphrase_counter() {

  const char_count = passphrase_field.value.length;
  
  if ( (char_count >= 1) && !passphrase_field.classList.contains('active') ) {
  
    passphrase_field.classList.add('active');
  
  } else if ( (char_count <= 0) ) {
  
    passphrase_field.classList.remove('active');
    
  }
  
  counter_el.textContent = char_count;

}
