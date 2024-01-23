


// Passphrase field with the has-counter class
const passphrase_field = document.querySelector('.field-wrap.field-passphrase .note-passphrase.has-counter');

// The element we will be targeting to update character count
const counter_el = document.querySelector('.field-wrap.field-passphrase .passphrase-char-count .cur-chars');

// Share secret URL <details> element
const share_url_details = document.querySelector('.note-share-url');






// Wait until HTML has been parsed
document.addEventListener('DOMContentLoaded', () => {
  

  document.body.classList.remove('no-js');


  // If the passphrase_field exists
  // Get ready to increment the counter
  if ( passphrase_field ) {
  
    // Update the counter on every keystroke
    passphrase_field.addEventListener('keyup', update_passphrase_counter);
    
  }
  
  
  
  if ( share_url_details ) {
  
    view_note_secret()
  
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

} // update_passphrase_counter()








// This could be a lot smarter.
// It would be nice if this could store an identifier
// for the note that was created.
function on_new_note_submit() {

 localStorage.setItem('created_new_note', true);

} // on_new_note_submit()






// If the visitor has the 'created_new_note' flag set 
// to true we assume the just created a new note, so
// we default the share url to open.
// Otherwise the share url defaults to closed.
function view_note_secret() {

  const created_new_note = localStorage.getItem("created_new_note");

  
  if (created_new_note === "true") {
  
    // Make sure the share_url details element exists.
    // If it does, open it.
    if ( share_url_details ) {
    
      share_url_details.open = true;
    
    }
    

  }


  // Delete the flag from local storage
  localStorage.removeItem("created_new_note");

}




