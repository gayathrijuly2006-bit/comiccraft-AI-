function showLoading(){
  const button=document.getElementById('generateBtn');
  const loading=document.getElementById('loading');
  if(button) { button.disabled=true; button.textContent='Generating…'; }
  if(loading) loading.hidden=false;
}
