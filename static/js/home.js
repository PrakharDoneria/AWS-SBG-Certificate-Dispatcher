export function initHome() {
  const rotating = document.getElementById('rotating-word');
  if (rotating) {
    const words = ['recognition.', 'momentum.', 'belonging.'];
    let index = 0;
    setInterval(() => {
      index = (index + 1) % words.length;
      rotating.animate(
        [{ opacity: 0, transform: 'translateY(8px)' }, { opacity: 1, transform: 'translateY(0)' }],
        { duration: 450 },
      );
      rotating.textContent = words[index];
    }, 2600);
  }

  const profile = document.getElementById('profile');
  const aboutProfile = document.getElementById('about-profile');
  (profile || aboutProfile) && fetch('/api/about')
    .then((response) => response.json())
    .then((user) => {
      if (profile) profile.innerHTML = `<img class="avatar-placeholder" src="${user.avatar_url || ''}" alt=""><div><b>${user.name || 'Prakhar Doneria'}</b><small>${user.html_url || 'github.com/PrakharDoneria'}</small></div>`;
      if (aboutProfile) {
        aboutProfile.innerHTML = `<img class="about-avatar" src="${user.avatar_url || ''}" alt=""><h2>${user.name || 'Prakhar Doneria'}</h2><p>${user.bio || 'A community builder making small tools that help people feel seen.'}</p>`;
        document.getElementById('about-summary').textContent = user.project?.description || 'An open source certificate dispatcher for community-led recognition.';
        document.getElementById('project-name').textContent = user.project?.name || 'AWS SBG Certificate Dispatcher';
        document.getElementById('project-description').textContent = user.project?.description || 'Personalize certificates, keep recipient lists local, and deliver each certificate through Gmail with a verification trail.';
        document.getElementById('project-link').href = user.project?.html_url || 'https://github.com/PrakharDoneria/AWS-SBG-Certificate-Dispatcher';
      }
    })
    .catch(() => {});
}