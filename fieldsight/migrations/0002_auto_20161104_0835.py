# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, verbose_name=b'Organization Type')),
            ],
        ),
        migrations.AddField(
            model_name='organization',
            name='additional_desc',
            field=models.TextField(null=True, verbose_name=b'Additional Description', blank=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='country',
            field=models.CharField(default='NPL', max_length=3, choices=[('AFG', 'Afghanistan'), ('ALA', '\xc5land Islands'), ('ALB', 'Albania'), ('DZA', 'Algeria'), ('ASM', 'American Samoa'), ('AND', 'Andorra'), ('AGO', 'Angola'), ('AIA', 'Anguilla'), ('ATA', 'Antarctica'), ('ATG', 'Antigua and Barbuda'), ('ARG', 'Argentina'), ('ARM', 'Armenia'), ('ABW', 'Aruba'), ('AUS', 'Australia'), ('AUT', 'Austria'), ('AZE', 'Azerbaijan'), ('BHS', 'Bahamas'), ('BHR', 'Bahrain'), ('BGD', 'Bangladesh'), ('BRB', 'Barbados'), ('BLR', 'Belarus'), ('BEL', 'Belgium'), ('BLZ', 'Belize'), ('BEN', 'Benin'), ('BMU', 'Bermuda'), ('BTN', 'Bhutan'), ('BOL', 'Bolivia, Plurinational State of'), ('BIH', 'Bosnia and Herzegovina'), ('BES', 'Bonaire, Sint Eustatius and Saba'), ('BWA', 'Botswana'), ('BVT', 'Bouvet Island'), ('BRA', 'Brazil'), ('IOT', 'British Indian Ocean Territory'), ('BRN', 'Brunei Darussalam'), ('BGR', 'Bulgaria'), ('BFA', 'Burkina Faso'), ('BDI', 'Burundi'), ('KHM', 'Cambodia'), ('CMR', 'Cameroon'), ('CAN', 'Canada'), ('CPV', 'Cape Verde'), ('CYM', 'Cayman Islands'), ('CAF', 'Central African Republic'), ('TCD', 'Chad'), ('CHL', 'Chile'), ('CHN', 'China'), ('CXR', 'Christmas Island'), ('CCK', 'Cocos (Keeling) Islands'), ('COL', 'Colombia'), ('COM', 'Comoros'), ('COG', 'Congo'), ('COD', 'Congo, The Democratic Republic of the'), ('COK', 'Cook Islands'), ('CRI', 'Costa Rica'), ('CIV', "C\xf4te d'Ivoire"), ('HRV', 'Croatia'), ('CUB', 'Cuba'), ('CUW', 'Cura\xe7ao'), ('CYP', 'Cyprus'), ('CZE', 'Czech Republic'), ('DNK', 'Denmark'), ('DJI', 'Djibouti'), ('DMA', 'Dominica'), ('DOM', 'Dominican Republic'), ('ECU', 'Ecuador'), ('EGY', 'Egypt'), ('SLV', 'El Salvador'), ('GNQ', 'Equatorial Guinea'), ('ERI', 'Eritrea'), ('EST', 'Estonia'), ('ETH', 'Ethiopia'), ('FLK', 'Falkland Islands (Malvinas)'), ('FRO', 'Faroe Islands'), ('FJI', 'Fiji'), ('FIN', 'Finland'), ('FRA', 'France'), ('GUF', 'French Guiana'), ('PYF', 'French Polynesia'), ('ATF', 'French Southern Territories'), ('GAB', 'Gabon'), ('GMB', 'Gambia'), ('GEO', 'Georgia'), ('DEU', 'Germany'), ('GHA', 'Ghana'), ('GIB', 'Gibraltar'), ('GRC', 'Greece'), ('GRL', 'Greenland'), ('GRD', 'Grenada'), ('GLP', 'Guadeloupe'), ('GUM', 'Guam'), ('GTM', 'Guatemala'), ('GGY', 'Guernsey'), ('GIN', 'Guinea'), ('GNB', 'Guinea-Bissau'), ('GUY', 'Guyana'), ('HTI', 'Haiti'), ('HMD', 'Heard Island and McDonald Islands'), ('VAT', 'Holy See (Vatican City State)'), ('HND', 'Honduras'), ('HKG', 'Hong Kong'), ('HUN', 'Hungary'), ('ISL', 'Iceland'), ('IND', 'India'), ('IDN', 'Indonesia'), ('IRN', 'Iran, Islamic Republic of'), ('IRQ', 'Iraq'), ('IRL', 'Ireland'), ('IMN', 'Isle of Man'), ('ISR', 'Israel'), ('ITA', 'Italy'), ('JAM', 'Jamaica'), ('JPN', 'Japan'), ('JEY', 'Jersey'), ('JOR', 'Jordan'), ('KAZ', 'Kazakhstan'), ('KEN', 'Kenya'), ('KIR', 'Kiribati'), ('PRK', "Korea, Democratic People's Republic of"), ('KOR', 'Korea, Republic of'), ('KWT', 'Kuwait'), ('KGZ', 'Kyrgyzstan'), ('LAO', "Lao People's Democratic Republic"), ('LVA', 'Latvia'), ('LBN', 'Lebanon'), ('LSO', 'Lesotho'), ('LBR', 'Liberia'), ('LBY', 'Libya'), ('LIE', 'Liechtenstein'), ('LTU', 'Lithuania'), ('LUX', 'Luxembourg'), ('MAC', 'Macao'), ('MKD', 'Macedonia, The Former Yugoslav Republic of'), ('MDG', 'Madagascar'), ('MWI', 'Malawi'), ('MYS', 'Malaysia'), ('MDV', 'Maldives'), ('MLI', 'Mali'), ('MLT', 'Malta'), ('MHL', 'Marshall Islands'), ('MTQ', 'Martinique'), ('MRT', 'Mauritania'), ('MUS', 'Mauritius'), ('MYT', 'Mayotte'), ('MEX', 'Mexico'), ('FSM', 'Micronesia, Federated States of'), ('MDA', 'Moldova, Republic of'), ('MCO', 'Monaco'), ('MNG', 'Mongolia'), ('MNE', 'Montenegro'), ('MSR', 'Montserrat'), ('MAR', 'Morocco'), ('MOZ', 'Mozambique'), ('MMR', 'Myanmar'), ('NAM', 'Namibia'), ('NRU', 'Nauru'), ('NPL', 'Nepal'), ('NLD', 'Netherlands'), ('ANT', 'Netherlands Antilles'), ('NCL', 'New Caledonia'), ('NZL', 'New Zealand'), ('NIC', 'Nicaragua'), ('NER', 'Niger'), ('NGA', 'Nigeria'), ('NIU', 'Niue'), ('NFK', 'Norfolk Island'), ('MNP', 'Northern Mariana Islands'), ('NOR', 'Norway'), ('OMN', 'Oman'), ('PAK', 'Pakistan'), ('PLW', 'Palau'), ('PSE', 'occupied Palestinian territory'), ('PAN', 'Panama'), ('PNG', 'Papua New Guinea'), ('PRY', 'Paraguay'), ('PER', 'Peru'), ('PHL', 'Philippines'), ('PCN', 'Pitcairn'), ('POL', 'Poland'), ('PRT', 'Portugal'), ('PRI', 'Puerto Rico'), ('QAT', 'Qatar'), ('REU', 'R\xe9union'), ('ROU', 'Romania'), ('RUS', 'Russian Federation'), ('RWA', 'Rwanda'), ('BLM', 'Saint Barth\xe9lemy'), ('SHN', 'Saint Helena, Ascension and Tristan da Cunha'), ('KNA', 'Saint Kitts and Nevis'), ('LCA', 'Saint Lucia'), ('MAF', 'Saint Martin (French part)'), ('SPM', 'Saint Pierre and Miquelon'), ('VCT', 'Saint Vincent and the Grenadines'), ('WSM', 'Samoa'), ('SMR', 'San Marino'), ('STP', 'S\xe3o Tom\xe9 and Pr\xedncipe'), ('SAU', 'Saudi Arabia'), ('SEN', 'Senegal'), ('SRB', 'Serbia'), ('SYC', 'Seychelles'), ('SLE', 'Sierra Leone'), ('SGP', 'Singapore'), ('SXM', 'Sint Maarten (Dutch part)'), ('SVK', 'Slovakia'), ('SVN', 'Slovenia'), ('SLB', 'Solomon Islands'), ('SOM', 'Somalia'), ('ZAF', 'South Africa'), ('SGS', 'South Georgia and the South Sandwich Islands'), ('ESP', 'Spain'), ('LKA', 'Sri Lanka'), ('SSD', 'South Sudan'), ('SDN', 'Sudan'), ('SUR', 'Suriname'), ('SJM', 'Svalbard and Jan Mayen'), ('SWZ', 'Swaziland'), ('SWE', 'Sweden'), ('CHE', 'Switzerland'), ('SYR', 'Syrian Arab Republic'), ('TWN', 'Taiwan, Province of China'), ('TJK', 'Tajikistan'), ('TZA', 'Tanzania, United Republic of'), ('THA', 'Thailand'), ('TLS', 'Timor-Leste'), ('TGO', 'Togo'), ('TKL', 'Tokelau'), ('TON', 'Tonga'), ('TTO', 'Trinidad and Tobago'), ('TUN', 'Tunisia'), ('TUR', 'Turkey'), ('TKM', 'Turkmenistan'), ('TCA', 'Turks and Caicos Islands'), ('TUV', 'Tuvalu'), ('UGA', 'Uganda'), ('UKR', 'Ukraine'), ('ARE', 'United Arab Emirates'), ('GBR', 'United Kingdom'), ('USA', 'United States'), ('UMI', 'United States Minor Outlying Islands'), ('URY', 'Uruguay'), ('UZB', 'Uzbekistan'), ('VUT', 'Vanuatu'), ('VEN', 'Venezuela, Bolivarian Republic of'), ('VNM', 'Viet Nam'), ('VGB', 'Virgin Islands, British'), ('VIR', 'Virgin Islands, U.S.'), ('WLF', 'Wallis and Futuna'), ('ESH', 'Western Sahara'), ('YEM', 'Yemen'), ('ZMB', 'Zambia'), ('ZWE', 'Zimbabwe')]),
        ),
        migrations.AddField(
            model_name='organization',
            name='public_desc',
            field=models.TextField(null=True, verbose_name=b'Public Description', blank=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='type',
            field=models.ForeignKey(default=1, verbose_name=b'Type of Organization', to='fieldsight.OrganizationType'),
            preserve_default=False,
        ),
    ]
