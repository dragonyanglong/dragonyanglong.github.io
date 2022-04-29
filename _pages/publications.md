---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---

<a href="{{ author.googlescholar }}">
You can also find my articles on <a href="{{ author.googlescholar }}" target="_blank">my Google Scholar profile</a>.

{% include base_path %}

{% for post in site.publications reversed %}
  {% include archive-single.html %}
{% endfor %}


