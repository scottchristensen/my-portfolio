(function () {
  function renderItem(project, isFeatured) {
    const subtitleClass = isFeatured ? "heading-small text-weight-regular" : "heading-xsmall text-weight-light";
    const item = document.createElement("div");
    item.setAttribute("role", "listitem");
    item.className = "work-collection-item w-dyn-item";
    item.innerHTML = `
      <a href="/work/${project.slug}" class="project-thumbnail-link w-inline-block">
        <div class="project-thumbnail-image-wrapper">
          <img src="${project.image}" loading="lazy" alt="${project.title}" width="1331" height="839" class="project-thumbnail-image">
        </div>
        <div class="project-title-div">
          <h3 class="heading-small">${project.title}</h3>
          <div class="heading-small"> →</div>
        </div>
        <div class="project-title-div margin-0">
          <h4 class="${subtitleClass}">${project.subtitle}</h4>
        </div>
      </a>
    `;
    return item;
  }

  function populate(listEl, projects, isFeatured) {
    if (!listEl) return;
    listEl.innerHTML = "";
    projects.forEach((p) => listEl.appendChild(renderItem(p, isFeatured)));
  }

  fetch("/data/work.json")
    .then((r) => r.json())
    .then((data) => {
      const wrappers = document.querySelectorAll("#work .work-collection_wrapper");
      if (wrappers.length < 2) return;
      const featuredWrapper = wrappers[0];
      const gridWrapper = wrappers[1];
      const featuredList = featuredWrapper.querySelector(".work-collection_list");
      const gridList = gridWrapper.querySelector(".work-collection_list");
      populate(featuredList, data.featured, true);
      populate(gridList, data.grid, false);
      // If a collection is empty, hide the whole wrapper so we don't leave gaps.
      if (!data.featured || data.featured.length === 0) featuredWrapper.style.display = "none";
      if (!data.grid || data.grid.length === 0) gridWrapper.style.display = "none";
      wrappers.forEach((w) => {
        const empty = w.querySelector(".w-dyn-empty");
        if (empty) empty.remove();
      });
    })
    .catch((err) => console.error("Failed to load work data", err));
})();
