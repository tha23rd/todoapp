const production = !process.env.ROLLUP_WATCH;
module.exports = {
    purge: [],
    darkMode: false, // or 'media' or 'class'
    theme: {
        colors: {
            whiteish: {
                DEFAULT: '#F3F6F9'
            },
            blackish: {
                DEFAULT: '#2A3234'
            },
            grayish: {
                DEFAULT: '#888F99'
            },
            greenish: {
                DEFAULT: '#7FB587'
            },
            redish: {
                DEFAULT: '#975460'
            }
        },
        fontFamily: {
            sans: ['Roboto']
        },
        extend: {},
    },
    variants: {
        extend: {},
    },
    plugins: [],
    future: {
        purgeLayersByDefault: true,
        removeDeprecatedGapUtilities: true,
    },
    purge: {
        content: [
            "./src/**/*.svelte",
        ],
        safelist: [
            'border-greenish',
            'text-greenish'
        ],
        enabled: production // disable purge in dev
    },
}
