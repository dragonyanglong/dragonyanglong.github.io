---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---
{{author.googlescholar}}
You can also find my articles on <a href="https://scholar.google.com/citations?user=H2mOKp8AAAAJ" target="_blank">my Google Scholar profile</a>.

{% include base_path %}

{% for post in site.publications reversed %}
  {% include archive-single.html %}
{% endfor %}


