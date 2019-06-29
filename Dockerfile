# MAINTENER ADRIEN MONTIGNEAUX
FROM php:7.2-fpm

RUN apt-get update && apt-get install -y unzip curl tar

# Add directory to /var/www/html in container
ADD app/ /var/www/html/

RUN pecl install mongodb &&  echo "extension=mongodb.so" > /usr/local/etc/php/conf.d/mongo.ini && mkdir /usr/local/etc/php/mods-available/ && echo "extension=mongodb.so" > /usr/local/etc/php/mods-available/mongodb.ini
RUN apt install -y libzip-dev
RUN docker-php-ext-install zip
# Install composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer
RUN composer --version
RUN cd /var/www/html/
RUN ls -l
RUN composer install
RUN composer update

WORKDIR /var/www/html

RUN php bin/console doctrine:mongodb:schema:update --force
RUN php bin/console doctrine:mongodb:fixtures:load

# Changer le fichier .env pour définir 


