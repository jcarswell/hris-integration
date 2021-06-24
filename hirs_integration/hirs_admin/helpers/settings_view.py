import logging

from django.utils.safestring import mark_safe

from hirs_admin import widgets

logger = logging.getLogger('hirs_admin.helpers.settings_view')

class Settings():

    def __init__(self,objects):
        self.items = {}
        self.update_catagories(objects)
        logger.warning(f"Data: {self.as_html}")

    def update_catagories(self,objects):
        for x in objects:
            cat = x.catagory
            if cat not in self.items:
                self.items[cat] = {
                    "name": x.catagory_text,
                    "groups": {}
                }
                logger.info(f"Added Catagory: {cat}")
            
            self.items[cat]["groups"] = self.update_group(self.items[cat]["groups"], x)
  
    def update_group(self, data, object):
        group = object.group
        if group not in data:
            data[group] = {
                "name": object.group_text,
                "items": {}
            }
            logger.info(f"Added group {group}")
        
        data[group]["items"] = self.update_item(data[group]["items"], object)
        
        return data


    def update_item(self,data, object):
        item = object.item

        if object.hidden:
            widget = widgets.Hidden
        else:
            widget = widgets.Item

        data[item] = {
            "title": object.item_text,
            "value": object.value,
            "widget": widget          
        }
        
        return data

    def as_nav(self):
        output = []
        for name,cat in self.items.items():
            output.append(
                f'<a class="list-group-item list-group-item-action" href="#{ name }">{ cat["name"] }</a>'
            )
            output.append('<nav class="nav nav-pills flex-column">')
            for name,group in cat["groups"].items():
                output.append(
                    f'<a class="nav-link ml-3 my-1" href="#{ name }">{ group["name"] }</a>'
                )
            output.append('</nav>')
        
        return mark_safe('\n'.join(output))
    
    def as_html(self):
        output = []
        for name,cat in self.items.items():
            output.append(f'<h3 id="{ name }">{ cat["name"] }</h3>')
            output.append('<hr style="border-top:2px solid #bbb">')
            for name,group in cat["groups"].items():
                output.append(
                    f'<h4 id="{ name}">{ group["name"] }</a>'
                )
                for id,item in group["items"].items():
                    output.append(item['widget']().render(
                        id,
                        item["value"],
                        item["title"]))

        return mark_safe('\n'.join(output))
    
    def __str__(self) -> str:
        self.as_html()