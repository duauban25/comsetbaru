// Auto Proper-Case for name inputs (id="name")
(function() {
  function toProperCaseName(raw) {
    if (!raw) return '';
    let s = String(raw).trim().replace(/\s+/g, ' ');
    return s.split(' ').map(word => {
      if (!word) return '';
      // Preserve all-uppercase acronyms (>=2 letters)
      if (/^[A-Z]{2,}$/.test(word)) return word;
      return word.split('-').map(part => {
        if (!part) return '';
        return part.split("'").map(seg => {
          if (!seg) return '';
          return seg.charAt(0).toUpperCase() + seg.slice(1).toLowerCase();
        }).join("'");
      }).join('-');
    }).join(' ');
  }

  function attachProperCaseBehavior(input) {
    if (!input || input._properCaseAttached) return;
    input._properCaseAttached = true;

    const format = () => { input.value = toProperCaseName(input.value); };

    // On blur
    input.addEventListener('blur', format);
    // On Enter key
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        format();
      }
    });
    // On form submit
    const form = input.closest('form');
    if (form) {
      form.addEventListener('submit', format);
    }
  }

  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('input#name').forEach(attachProperCaseBehavior);
  });
})();

// -- Search Birthdates Modal wiring --
document.addEventListener('DOMContentLoaded', function() {
  const modal = document.getElementById('search-birthdates-modal');
  const openBtn = document.getElementById('open-search-birthdates');
  const openBtnMobile = document.getElementById('open-search-birthdates-mobile');
  const closeBtn = document.getElementById('close-search-birthdates');
  const form = document.getElementById('search-birthdates-form');
  const statusEl = document.getElementById('search-birthdates-status');
  const resultsContainer = document.getElementById('search-birthdates-results');
  const listEl = document.getElementById('search-birthdates-list');

  function openModal() {
    if (!modal) return;
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    if (statusEl) statusEl.textContent = '';
    if (listEl) listEl.innerHTML = '';
    if (resultsContainer) resultsContainer.classList.add('hidden');

    // Prefill defaults
    try {
      // Set Hari to today's system day
      var hariSel = form ? form.querySelector('select[name="hari"]') : null;
      if (hariSel) {
        var mapHari = ['Minggu','Senin','Selasa','Rabu','Kamis','Jumat','Sabtu'];
        var today = new Date();
        var hariNow = mapHari[today.getDay()];
        if (Array.from(hariSel.options).some(o => o.value === hariNow)) {
          hariSel.value = hariNow;
        }
      }
      // Set Year to current year if empty
      var yearInput = form ? form.querySelector('input[name="year"]') : null;
      if (yearInput && (!yearInput.value || yearInput.value.trim() === '')) {
        yearInput.value = String(new Date().getFullYear());
      }
    } catch(e) { /* ignore */ }
  }

  function closeModal() {
    if (!modal) return;
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }

  if (openBtn) openBtn.addEventListener('click', openModal);
  if (openBtnMobile) openBtnMobile.addEventListener('click', openModal);
  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (modal) {
    modal.addEventListener('click', function(e) { if (e.target === modal) closeModal(); });
  }

  if (form) {
    form.addEventListener('submit', async function(e) {
      e.preventDefault();
      if (statusEl) statusEl.textContent = 'Mencari...';
      if (listEl) listEl.innerHTML = '';
      if (resultsContainer) resultsContainer.classList.add('hidden');
      try {
        const fd = new FormData(form);
        const payload = {
          year: fd.get('year') ? parseInt(fd.get('year'), 10) : undefined,
          hari: fd.get('hari'),
          pasaran: fd.get('pasaran'),
          wuku: fd.get('wuku')
        };
        const resp = await fetch('/api/search_birthdates', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        const data = await resp.json();
        if (data && data.success && Array.isArray(data.dates)) {
          if (statusEl) statusEl.textContent = 'Ditemukan: ' + (data.count ?? data.dates.length);
          if (resultsContainer) resultsContainer.classList.remove('hidden');
          if (listEl) {
            data.dates.forEach(d => {
              const li = document.createElement('li');
              li.textContent = d.display || d.iso || '';
              listEl.appendChild(li);
            });
          }
        } else {
          if (statusEl) statusEl.textContent = 'Tidak ada hasil.';
        }
      } catch (err) {
        if (statusEl) statusEl.textContent = 'Terjadi kesalahan.';
        console.error(err);
      }
    });
  }
});
