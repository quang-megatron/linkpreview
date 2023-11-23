from os.path import dirname

from previewlink_helper.helpers import LazyAttribute, titleize
from previewlink_helper.link import Link
from previewlink_helper.preview import Generic, OpenGraph


class LinkPreview:
    def __init__(self, link: Link, parser: str = "html.parser"):
        self.link = link
        self.generic = Generic(link, parser)
        self.opengraph = OpenGraph(link, parser)
        self.sources = (
            self.opengraph,
            self.generic,
        )

    def _find_attribute(self, name):
        for obj in self.sources:
            value = getattr(obj, name)
            if value:
                return value

    @LazyAttribute
    def site_name(self):
        return self._find_attribute("site_name")

    @LazyAttribute
    def title(self):
        return self._find_attribute("title")

    @LazyAttribute
    def description(self):
        return self._find_attribute("description")

    @LazyAttribute
    def image(self):
        return self._find_attribute("image")

    def _get_absolute_image(self, image):
        # is starts with url scheme
        parts = image.split("://")
        if len(parts) > 1 and image.startswith(parts[0]):
            return image

        link = self.link.copy()

        if image.startswith("/"):
            # image is located from root
            link.path = image

        elif link.path.endswith("/"):
            # the link is a directory
            link.path = "%s%s" % (link.path, image)

        else:
            # the link is a file
            link.path = "%s/%s" % (dirname(link.path), image)

        return link.url

    @LazyAttribute
    def absolute_image(self):
        if not self.image:
            return self.image

        return self._get_absolute_image(self.image)

    @LazyAttribute
    def force_title(self):
        if self.title:
            return self.title

        if self.link.may_file:
            exploded = self.link.path.split("/")[-1].split(".")
            if len(exploded) > 1:
                return titleize(".".join(exploded[:-1]))

        link = self.link.copy()
        link.netloc = link.netloc.split("@")[-1]
        return link.url[len(self.link.scheme) + 3 :]

    @LazyAttribute
    def favicon(self):
        return tuple(self.generic.favicon)

    @LazyAttribute
    def absolute_favicon(self):
        return tuple(
            map(
                lambda x: (self._get_absolute_image(x[0]), x[1], x[2]),
                self.favicon,
            )
        )

    def to_dict(self):
        return dict(
            site_name=self.site_name,
            title=self.title,
            description=self.description,
            image=self.image,
            absolute_image=self.absolute_image,
            force_title=self.force_title,
            favicon=self.favicon,
            absolute_favicon=self.absolute_favicon,
        )
