// WareVisor Login Controller
document.addEventListener('DOMContentLoaded', () => {

  if (window.lucide) {
    lucide.createIcons();
  }

  const rolePresets = {
    manager: {
      title: 'Central Manager',
      user: 'manager',
      pass: 'manager123'
    },
    sender: {
      title: 'Product Sender',
      user: 'sender',
      pass: 'sender123'
    }
  };

  let currentRole = 'manager';

  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');
  const rolePills = document.querySelectorAll('.role-pill-btn');
  const demoLoginBtn = document.getElementById('demo-login-btn');
  const demoBtnText = document.getElementById('demo-btn-text');
  const loginForm = document.getElementById('login-form');
  const submitBtn = document.getElementById('submit-btn');
  const togglePasswordBtn = document.getElementById('toggle-password');
  const eyeIcon = document.getElementById('eye-icon');
  const themeToggleBtn = document.getElementById('theme-toggle');

  // Role Pill Switcher
  rolePills.forEach(pill => {
    pill.addEventListener('click', () => {
      rolePills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      currentRole = pill.getAttribute('data-role');
      
      const preset = rolePresets[currentRole];
      usernameInput.value = preset.user;
      passwordInput.value = preset.pass;
      demoBtnText.textContent = `1-Click Login as ${preset.title}`;
    });
  });

  // Password Visibility Toggle
  togglePasswordBtn.addEventListener('click', () => {
    const isPass = passwordInput.getAttribute('type') === 'password';
    passwordInput.setAttribute('type', isPass ? 'text' : 'password');
    eyeIcon.setAttribute('data-lucide', isPass ? 'eye-off' : 'eye');
    if (window.lucide) lucide.createIcons();
  });

  // 1-Click Demo Login
  demoLoginBtn.addEventListener('click', () => {
    performLogin(rolePresets[currentRole].user, rolePresets[currentRole].title);
  });

  // Form Submit Login
  loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const u = usernameInput.value.trim();
    if (!u || !passwordInput.value) {
      showToast('Please enter username and password.', 'error');
      return;
    }
    performLogin(u, rolePresets[currentRole].title);
  });

  function performLogin(username, roleTitle) {
    submitBtn.innerHTML = '<span>Signing In...</span>';
    submitBtn.disabled = true;

    setTimeout(() => {
      const sessionData = {
        username: username,
        role: currentRole,
        roleTitle: roleTitle,
        authenticatedAt: new Date().toISOString()
      };
      sessionStorage.setItem('warevisor_session', JSON.stringify(sessionData));
      
      showToast(`Welcome! Logging into Dashboard...`, 'success');

      setTimeout(() => {
        window.location.href = 'index.html';
      }, 500);
    }, 600);
  }

  // Theme Toggle
  themeToggleBtn.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
  });

  function showToast(msg, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
  }

  // Particle Background
  const canvas = document.getElementById('ambient-canvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const particles = [];
    for (let i = 0; i < 35; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: Math.random() * 2 + 1,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4
      });
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach(p => {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(99, 102, 241, 0.3)';
        ctx.fill();
      });
      requestAnimationFrame(draw);
    }
    draw();
  }

});
