# Default configuration filtering for _Home Assistant_
> Filter out `default_config` without eliminating intruding into configuration.yaml.
> 
> &gt;= Home Assistant 2021.8.0
> 
>[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
>[![License](https://img.shields.io/badge/%D0%9B%D0%B8%D1%86%D0%B5%D0%BD%D0%B7%D0%B8%D1%8F-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
>[![Maintained?](https://img.shields.io/badge/%D0%9F%D0%BE%D0%B4%D0%B4%D0%B5%D1%80%D0%B6%D0%B8%D0%B2%D0%B0%D0%B5%D1%82%D1%81%D1%8F%3F-%D0%B4%D0%B0-green.svg)](https://github.com/alryaz/hass-default-config-filter/graphs/commit-activity)  
>
>[![Yandex Donation](https://img.shields.io/badge/%D0%9F%D0%BE%D0%B6%D0%B5%D1%80%D1%82%D0%B2%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-Yandex-red.svg)](https://money.yandex.ru/to/410012369233217)  
>[![PayPal Donation](https://img.shields.io/badge/%D0%9F%D0%BE%D0%B6%D0%B5%D1%80%D1%82%D0%B2%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-Paypal-blueviolet.svg)](https://www.paypal.me/alryaz)

>  ⚠️ This component is a Work-In-Progress-Alpha. Multiple things might change. Initial release works
> on certain scenarios, however it is never guaranteed it won't break your system. Proceed with
> extreme caution.



## _Y tho?_

I develop components for Home Assistant frequently that I personally like to use, and sometimes
the overhead that they generate is too heavy for my Home Assistant installation. Additionally,
I don't utilize some of HA's embedded components such as `cloud`, `input_boolean` and several
others.

_&mdash; Why not simply remove `default_config` from configuration.yaml?_
... is a valid question, to which I answer: I learnt about the availability of the
`energy` component almost three months since its release to stable. This integration should
help me avoid encountering such mishaps in the future.

This component generates a new pseudo-custom component inside your `custom_components` directory
which mirrors `default_config`'s functionality almost entirely, but with a twist: the manifest
file that describes all the dependencies is reduced via provided blacklists. Therefore, on
every `default_config`'s update you will get all its components minus ones blacklisted. _Exactly
something I require._

## Installation
1. Install [HACS](https://hacs.xyz/docs/installation/manual)
2. Add new custom repository: `https://github.com/alryaz/hass-default-config-filter`
3. Install available `Default Configuration Filter` component
4. Configure using one of the available methods

## Configuration

> ⚠️ This assumes the component has already been installed!

### Via _Integrations_ interface

> ℹ️ Lack of `config` integration in selections is not a bug. You will lock yourself out should
> you be tempted to use it.

The easiest method of installing is through GUI (options etc. supported)

[![Configure default_config_filter integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=default_config_filter)
<small>(Alternatively, open _Settings_ &#8594; _Integrations_ &#8594; _Add new integration_ &#8594; _Default Config Filter_)</small>

### Using `configuration.yaml`

The following  

```yaml
default_config:  # this might remain as-is, but must be present
...
default_config_filter:
  cloud: true  # `true` means this component will be removed from default_config's dependencies
  ffmpeg: false  # `false` means this component will remain untouched
```

Alternative method:
```yaml
default_config:
...
default_config_filter: ['cloud', 'input_boolean', 'stream']
```
