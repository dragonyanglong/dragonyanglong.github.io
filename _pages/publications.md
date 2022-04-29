---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---
{{author.googlescholar}}
You can also find my articles on <a href="{{author.googlescholar}}" target="_blank"><u>my Google Scholar profile</u></a>.
      <p>DOI: <a href="https://dx.doi.org/{{ post.doi }}"><u>{{ post.doi }}</u></a></p>

{% include base_path %}

{% for post in site.publications reversed %}
  {% include archive-single.html %}
{% endfor %}


