
    $(document).ready(function(){
        $('.login-info-box').fadeOut();
        $('.login-show').addClass('show-log-panel');
    });
    /* When the user clicks on the button,
    toggle between hiding and showing the dropdown content */
    function myFunction() {
        document.getElementById("myDropdown").classList.toggle("show");
    }
    
    // Close the dropdown menu if the user clicks outside of it
    window.onclick = function(event) {
        if (!event.target.matches('.dropbtn')) {
        var dropdowns = document.getElementsByClassName("dropdown-content");
        var i;
        for (i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
            openDropdown.classList.remove('show');
            }
        }
        }
    }

    // 403 Error Page
    const interval = 500;
    function generateLocks() {
    const lock = document.createElement('div'),
            position = generatePosition();
    lock.innerHTML = '<div class="top"></div><div class="bottom"></div>';
    lock.style.top = position[0];
    lock.style.left = position[1];
    lock.classList = 'lock'// generated';
    document.body.appendChild(lock);
    setTimeout(()=>{
        lock.style.opacity = '1';
        lock.classList.add('generated');
    }, 100);
    setTimeout(()=>{
        lock.parentElement.removeChild(lock);
    }, 2000);
    }
    function generatePosition() {
        const x = Math.round((Math.random() * 100) - 10) + '%';
        const y = Math.round(Math.random() * 100) + '%';
    return [x,y];
    }
    setInterval(generateLocks,interval);
    generateLocks();

      
    