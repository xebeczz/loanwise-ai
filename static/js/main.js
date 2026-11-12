/* LoanWise AI - shared client-side helpers. */
function togglePassword(inputId, btn) {
  var input = document.getElementById(inputId);
  if (!input) return;
  var show = input.type === 'password';
  input.type = show ? 'text' : 'password';
  var icon = btn.querySelector('.material-symbols-outlined');
  if (icon) icon.textContent = show ? 'visibility_off' : 'visibility';
}
