from django.db import models

class noticias(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    site_icon = models.URLField(max_length=200)
    link = models.URLField(max_length=200, unique=True)  
    image = models.URLField(max_length=200, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "noticia"
        verbose_name_plural = "noticias"
        ordering = ['-fecha']

    def __str__(self):
        return self.titulo