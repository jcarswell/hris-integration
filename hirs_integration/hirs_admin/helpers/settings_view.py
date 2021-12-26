import logging

from django.utils.safestring import mark_safe

from hirs_admin import widgets as w

logger = logging.getLogger('hirs_admin.settings_view')

class Settings():

    def __init__(self,objects):
        self.items = {}
        self.update_groups(objects)

    def update_groups(self,objects):
        output = {}
        for x in objects:
            group = x.group
            if group not in output:
                output[group] = {
                    "name": x.group_text,
                    "catagories": {}
                }
                logger.debug(f"Added Catagory: {group}")
            
            output[group]["catagories"] = self.update_catagories(output[group]["catagories"], x)
            
        for x in sorted(output):
            self.items[x] = output[x]
  
    def update_catagories(self, data, object):
        cat = object.catagory
        if cat not in data:
            data[cat] = {
                "name": object.catagory_text,
                "items": {}
            }
            logger.debug(f"Added group {cat}")
        
        data[cat]["items"] = self.update_item(data[cat]["items"], object)
        
        return data


    def update_item(self,data, object):
        item = object.pk

        if object.hidden:
            widget = w.Hidden
        else:
            widget = w.Item

        data[item] = {
            "title": object.item_text,
            "value": object.value,
            "widget": widget
        }
        
        return data

    def as_nav(self):
        output = []
        for gname,group in self.items.items():
            output.append(
                f'<a class="list-group-item list-group-item-action" href="#{gname}">{ group["name"] }</a>'
            )
            output.append('<nav class="nav nav-pills flex-column">')
            for cname,cat in group["catagories"].items():
                output.append(
                    f'<a class="nav-link ml-3 my-1" href="#{gname}_{cname}">{cat["name"]}</a>'
                )
            output.append('</nav>')
        
        return mark_safe('\n'.join(output))
    
    def as_html(self):
        output = []
        for gname,group in self.items.items():
            output.append(f'<h3 id="{gname}">{group["name"]}</h3>')
            output.append('<hr style="border-top:2px solid #bbb">')
            for cname,cat in group["catagories"].items():
                output.append(
                    f'<h4 id="{gname}_{cname}">{cat["name"]}</a>'
                )
                for id,item in cat["items"].items():
                    wgt = item['widget']()
                    wgt.title = item["title"]
                    output.append(wgt.render(id,item["value"],None))

        return mark_safe('\n'.join(output))
    
    def __str__(self) -> str:
        self.as_html()