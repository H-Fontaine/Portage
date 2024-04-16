#include "stm32f4xx.h"

#define PIN_MAIN_TRIGGER 15
#define PIN_AUX_TRIGGER 14
#define HSI_FREQ 16
// TODO (ALL FIRMWARES) THIS SHOULD BE A VARIABLE
#define HSE_FREQ 10

// RIGHT BEFORE 7.2.1
#define APB1_MAX 42
#define APB2_MAX 84

#define WS_N 6
uint8_t ws_ranges[WS_N] = {30, 60, 90, 120, 150, 168};


//USER CONFIGURABLE VARIABLES
#define USE_HSI 1
#define F_SYSCLK 168
#define WAIT_STATES 5
#define ENABLE_CACHES 0
#define ENABLE_ART 0

//MIGHT WANT TO INITIALIZE THESE VARIABLES USING GDB - START
uint8_t clock_check = 0;
uint8_t use_hsi = USE_HSI;
uint8_t f_sysclk = F_SYSCLK;
uint8_t wait_states = WAIT_STATES;
uint8_t enable_caches = ENABLE_CACHES;
uint8_t enable_art = ENABLE_ART;
// INITIALIZE THESE VARIABLES USING GDB - END

void init_SYSCLK(uint8_t use_hsi, uint8_t f_sysclk, uint8_t wait_states, uint8_t enable_caches) {
    // MORE INFO ABOUT CLOCKS IN 7.2 (CLOCK TREE)
    //
    // @ STARTUP, BOARD RUNS ON HSI
    //
    // PLLCLK = (PLL_INPUT / PLLM) * PLLN / PLLP
    // PLL CONFIGURATION - BE CAREFUL :
    // 50 <= PLLN <= 432. MIN STEP FOR FULL RANGE: 168/432=0.39MHZ
    // PLLP = 2 (0b00), 4 (0b01), 6 (0b10), 8 (0b11)
    // 2 <= PLLM <= 63 -- MUST BE SET SO THAT VCO INPUT IS IN
    //                    1MHZ-2MHZ (DATASHEET - 2MHZ IS BEST, 
    //                    TYPICAL VALUE)

    if (f_sysclk > 144) { // MAX IS 168MHZ
        // ENABLE ACCESS THE PWR MODULE (7.3.13)
        RCC->APB1ENR |= RCC_APB1ENR_PWREN;

        // RAMP UP THE POWER SUPPLY (5.1.3) IN ORDER TO BE ABLE
        // TO INCREASE THE SYSTEM CLOCK TO 168MHZ (3.5.1)
        PWR->CR &= ~PWR_CR_VOS_Msk;
        while (!(PWR->CSR & PWR_CSR_VOSRDY));
    }

    // WHEN USING THE PLL, CONFIGURE IT TO ALLOW FOR BEST 
    // GRANULARITY IN THE OUTPUT (BEST MATCH WITH DESIRED f_sysclk)
    uint8_t use_pll = 0;
    // FOR FREQUENCIES BELOW HSI_FREQ, USE HSE (WHICH I CONFIGURE
    // SO AS TO BE SLOWER THAN HSI - PROVIDES FINER CONTROL
    // OVER THE FREQUENCY OF PLLCLK: (ARBITRARILY, WITHIN THE
    // LIMITS OF PLL_INPUT) SMALLER STEPS)
    //
    // LOGIC FOR PLL FACTORS:
    //
    // PLLP IS ALWAYS SET TO ITS MAXIMUM VALUE (8 - ALLOWS FOR 
    // BEST PRECISION ON THE DESIRED FREQUENCY, CANNOT GET SMALLER 
    // STEPS), PLLM IS SET TO ENSURE THAT THE VCO INPUT IS WITHIN 
    // THE RECOMMENDED RANGE. BASED ON THESE TWO FACTORS, A 
    // MAXIMUM ACHIEVABLE FREQUENCY IS COMPUTED USING THE MAXIMUM 
    // VALUE FOR PLLN, AND I THEN DECREASE PLLP UNTIL I COVER 
    // THE DESIRED FREQUENCIES RANGE FOR f_sysclk
    //
    // NOTE: SINCE I DO NOT WANT TO USE FLOATING POINT ARITHMETIC,
    // IT IS WISER TO CHOOSE FACTORS OF THE FORM 2^N. COMPUTING
    // THE SCALING FACTOR FOR f_sysclk IS THEN A MATTER OF SHIFTING
    if (use_hsi) {
        if (HSI_FREQ > f_sysclk) {
            // FORCE THE USER TO USE HSE
            uint8_t dummy = *((uint8_t *)0);
            (void)dummy;
        }
        // ON THE STM32F4[0/1]7, HSI IS AT 16MHZ
        if (HSI_FREQ < f_sysclk) {
            // USER HAS REQUESTED A NEW FREQUENCY. I HAVE TO
            // USE THE PLL
            use_pll = 1;

            //
            // CONFIGURE THE PLL (7.3.2)
            //

            // HSI RUNS @16MHZ
            // (STEP: ABOVE_THRESHOLD > BELOW_THRESHOLD)
            //         16/(8*4) = 0.5 > 16/(8*8) = 0.25
            // (MAX_F(32) 0.5*432 = 216 > MAX_F(64) 0.25*432 = 108)

            // PLLQ : LEFT AS-IS -- DOES NOT MATTER
            // PLLSRC : LEFT AS-IS, HSI (0)
            // PLLM : 8 -- 2MHZ IN
            RCC->PLLCFGR &= ~RCC_PLLCFGR_PLLM_Msk;
            RCC->PLLCFGR |= (8 << RCC_PLLCFGR_PLLM_Pos);

            uint16_t scaling;
            if (f_sysclk <= 108) {
                // PLLP : 8
                RCC->PLLCFGR &= ~RCC_PLLCFGR_PLLP_Msk;
                RCC->PLLCFGR |= RCC_PLLCFGR_PLLP_Msk;

                scaling = f_sysclk * 4;
            } else {
                // PLLP : 4
                RCC->PLLCFGR &= ~RCC_PLLCFGR_PLLP_Msk;
                RCC->PLLCFGR |= 1 << RCC_PLLCFGR_PLLP_Pos;

                scaling = f_sysclk * 2;
            }
            // PLLN : PREVIOUSLY COMPUTED SCALING FACTOR
            // f_sysclk OUT
            RCC->PLLCFGR &= ~RCC_PLLCFGR_PLLN_Msk;
            RCC->PLLCFGR |= ((scaling & 0x1FF) << RCC_PLLCFGR_PLLN_Pos);
        }
    } else {
        // TURN HSE ON (6.2.1)
        //
        // SET HSEBYP ONLY WHEN CLOCK CAN BE GIVEN ON ONE PIN
        // E.G - DOES NOT COME FROM CRYSTAL ON BOARD, I.E THIS 
        // IS OUR USE CASE -- CLOCK COMES WAVEFORM GENERATOR @F
        // MHZ
        RCC->CR |= (RCC_CR_HSEON | RCC_CR_HSEBYP);
        while (!(RCC->CR & RCC_CR_HSERDY));

        if (HSE_FREQ != f_sysclk) {
            // USER HAS REQUESTED A NEW FREQUENCY. I HAVE TO
            // USE THE PLL
            use_pll = 1;

            //
            // CONFIGURE THE PLL (7.3.2)
            //

            // HSE RUNS @F MHZ
            // (STEP: ABOVE_THRESHOLD > BELOW_THRESHOLD)
            //                F/(4*M) > F/(8*M)
            // (MAX_F(4*M) F*108/M > MAX_F(8*M) F*54/M)
            // E.G: HSE = 10MHZ
            //                   (0.5 > 0.25)
            // (MAX_F(20) 216 > MAX_F(10) 108)
            //
            // THE USER MAY CONTROL TARGET FREQUENCY PRECISION BY
            // CHANGING HSE (INCREASING HSE ALLOWS THE USER TO
            // INCREASE /M UNTIL IT REACHES ITS MAXIMUM VALUE, AT
            // WHICH POINT, HIGHER INPUT FREQUENCIES DO NOT FEATURE
            // ANY ADVANTAGE)

            // PLLQ : LEFT AS-IS -- DOES NOT MATTER
            // PLLSRC : HSE (1) -- 10MHZ
            // PLLM : 5 -- 2MHZ IN
            // TODO (ALL FIRMWARES) COMPUTE PLLM AND FREQ THRESHOLDS AS A FUNCTION OF HSE_FREQ
            RCC->PLLCFGR |= RCC_PLLCFGR_PLLSRC_HSE;
            RCC->PLLCFGR &= ~RCC_PLLCFGR_PLLM_Msk;
            RCC->PLLCFGR |= (5 << RCC_PLLCFGR_PLLM_Pos);

            uint16_t scaling;
            if (f_sysclk <= 108) {
                // PLLP : 8
                RCC->PLLCFGR &= ~RCC_PLLCFGR_PLLP_Msk;
                RCC->PLLCFGR |= RCC_PLLCFGR_PLLP_Msk;

                scaling = f_sysclk * 4;
            } else {
                // PLLP : 4
                RCC->PLLCFGR &= ~RCC_PLLCFGR_PLLP_Msk;
                RCC->PLLCFGR |= 1 << RCC_PLLCFGR_PLLP_Pos;

                scaling = f_sysclk * 2;
            }
            // PLLN : PREVIOUSLY COMPUTED SCALING FACTOR
            // f_sysclk OUT
            RCC->PLLCFGR &= ~RCC_PLLCFGR_PLLN_Msk;
            RCC->PLLCFGR |= ((scaling & 0x1FF) << RCC_PLLCFGR_PLLN_Pos);
        }
    }

    // NOW CONFIGURE THE PRESCALERS WHICH FOLLOW SO THAT THE
    // CORRESPONDING FREQUENCIES REMAIN BELOW THE STATED 
    // LIMITS (7.3.3)
    //
    // AHB : LEFT AS-IS -- DO NOT PRESCALE CPU CLOCK
    // APB1, APB2 : COMPUTED BASED ON f_sysclk AND MAXIMUMS
    uint8_t div = 0;
    while ((f_sysclk >> div) > APB1_MAX) {
        div += 1;
    }
    if (div) {
        RCC->CFGR &= ~RCC_CFGR_PPRE1_Msk;
        RCC->CFGR |= ((3 + div) << RCC_CFGR_PPRE1_Pos);
    }

    div = 0;
    while ((f_sysclk >> div) > APB2_MAX) {
        div += 1;
    }
    if (div) {
        RCC->CFGR &= ~RCC_CFGR_PPRE2_Msk;
        RCC->CFGR |= ((3 + div) << RCC_CFGR_PPRE2_Pos);
    }

    if (use_pll) {
        // ENABLE THE NEW CLOCK PATH AND WAIT UNTIL IT IS EFFECTIVE
        // (7.3.1)
        RCC->CR |= RCC_CR_PLLON;
        while (!(RCC->CR & RCC_CR_PLLRDY));
    }

    //
    // NOW CONFIGURE THE FLASH SO THAT IT IS ABLE TO KEEP UP
    // WITH THE CPU (3.9.1)
    //

    if (enable_caches) {
        // ENABLE ALL CACHES (FASTER ACCESS)
        FLASH->ACR |= (FLASH_ACR_ICEN | FLASH_ACR_DCEN);

        if (enable_art) {
            // ART ACCELERATOR (3.5.2)
            // CAUSES A SPIKE FOR MIRACL::FF::BIG_XXX_bit
            // WEIRD BEHAVIOR -- DEPENDS ON NUMBER OF WAIT STATES
            FLASH->ACR |= FLASH_ACR_PRFTEN;
        }
    }

    // CHANGE LATENTCY (SINCE I CHANGED THE CPU FREQUENCY)
    // SEE TABLE 10 FOR THE NUMBER OF WAIT STATES AND WAIT UNTIL
    // THE CHANGE IS EFFECTIVE (THEN I KNOW THAT THE CACHES ARE
    // ENABLED AS WELL SINCE I DID THIS BEFORE)
    uint8_t min_ws = 0;
    for (uint8_t i = 0; i < WS_N; i++) {
        if (f_sysclk <= ws_ranges[i]) {
            min_ws = i;
            break;
        }
    }
    // MAKE SURE THAT wait_states IS BIG ENOUGH
    if (min_ws > wait_states) {
        // TRIGGER A FAULT TO FORCE THE USER TO CHANGE wait_states
        uint8_t dummy = *((uint8_t *)0);
        (void)dummy;
    }

    if (wait_states) {
        FLASH->ACR |= wait_states;
        while (!(FLASH->ACR & wait_states));
    }

    // SET CORRECT(1) OUTPUT AS THE SYSTEM CLOCK SOURCE AND WAIT
    // UNTIL IT IS EFFECTIVE (7.3.3) - (1) : BASED ON PREVIOUS
    // LOGIC
    if (use_pll) {
        RCC->CFGR &= ~RCC_CFGR_SW_Msk;
        RCC->CFGR |= RCC_CFGR_SW_1;
        while (!(RCC->CFGR & RCC_CFGR_SWS_1));
    } else {
        if (!(use_hsi)) {
            RCC->CFGR &= ~RCC_CFGR_SW_Msk;
            RCC->CFGR |= RCC_CFGR_SW_0;
            while (!(RCC->CFGR & RCC_CFGR_SWS_0));
        }
    }
}

void board_init() {
    init_SYSCLK(use_hsi, f_sysclk, wait_states, enable_caches);
}