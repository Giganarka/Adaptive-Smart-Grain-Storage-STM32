/* USER CODE BEGIN Header */
/*
 * Adaptive Smart Grain Storage System
 * STM32F103C8 + Proteus Simulation
 */
/* USER CODE END Header */

#include "main.h"
#include <stdio.h>
#include <string.h>
#include "lcd_i2c.h"

/* Private variables */
ADC_HandleTypeDef hadc1;
I2C_HandleTypeDef hi2c1;
TIM_HandleTypeDef htim1;
TIM_HandleTypeDef htim2;
UART_HandleTypeDef huart1;

char uart_buf[128];
uint16_t moisture_adc = 0;
uint16_t co2_adc      = 0;
float moisture_pct    = 0;
float co2_pct         = 0;
float temperature     = 25.0;
float humidity        = 60.0;
float csri            = 0;
uint8_t pir_state     = 0;
char status_msg[20];

/* Function prototypes */
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_ADC1_Init(void);
static void MX_I2C1_Init(void);
static void MX_TIM1_Init(void);
static void MX_TIM2_Init(void);
static void MX_USART1_UART_Init(void);

/* Helper functions */
uint16_t Read_ADC(uint32_t channel)
{
    ADC_ChannelConfTypeDef sConfig = {0};
    sConfig.Channel      = channel;
    sConfig.Rank         = ADC_REGULAR_RANK_1;
    sConfig.SamplingTime = ADC_SAMPLETIME_71CYCLES_5;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);
    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, 100);
    return HAL_ADC_GetValue(&hadc1);
}

void Fan_SetSpeed(uint8_t percent)
{
    uint32_t pwm = (htim2.Init.Period * percent) / 100;
    __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_3, pwm);
}

/* Main */
int main(void)
{
    HAL_Init();
    SystemClock_Config();

    MX_GPIO_Init();
    MX_ADC1_Init();
    MX_I2C1_Init();
    MX_TIM1_Init();
    MX_TIM2_Init();
    MX_USART1_UART_Init();

    HAL_ADCEx_Calibration_Start(&hadc1);

    lcd_init();
    lcd_put_cur(0, 0);
    lcd_send_string("SMART STORAGE");
    lcd_put_cur(1, 0);
    lcd_send_string("SYSTEM READY");
    HAL_Delay(2000);
    lcd_send_cmd(0x01);

    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_3);

    /* L293D direction: maju */
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_SET);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, GPIO_PIN_RESET);

    /* Relay awal OFF */
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_11, GPIO_PIN_RESET);

    /* Startup message UART */
    char start_msg[] = "SMART STORAGE SYSTEM READY\r\n";
    HAL_UART_Transmit(&huart1, (uint8_t*)start_msg, strlen(start_msg), 1000);

    while (1)
    {
        /* Baca ADC */
        moisture_adc = Read_ADC(ADC_CHANNEL_0);
        co2_adc      = Read_ADC(ADC_CHANNEL_1);
        moisture_pct = ((float)moisture_adc / 4095.0f) * 100.0f;
        co2_pct      = ((float)co2_adc      / 4095.0f) * 100.0f;

        /* Baca PIR */
        pir_state = HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_2);

        /* Simulasi suhu & kelembaban */
        temperature += 0.1f;
        if (temperature > 40.0f) temperature = 24.0f;

        humidity += 0.3f;
        if (humidity > 85.0f) humidity = 55.0f;

        /* Hitung CSRI */
        float temp_score;
        if (temperature <= 25.0f)
            temp_score = 0.0f;
        else if (temperature >= 40.0f)
            temp_score = 100.0f;
        else
            temp_score = ((temperature - 25.0f) / 15.0f) * 100.0f;

        csri = (0.40f * moisture_pct)
             + (0.30f * co2_pct)
             + (0.20f * temp_score)
             + (0.10f * (pir_state ? 100.0f : 0.0f));

        /* Logika status */
        if (csri < 30.0f)
        {
            strcpy(status_msg, "SAFE");
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_15, GPIO_PIN_SET);   /* LED Hijau ON */
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_14, GPIO_PIN_RESET); /* LED Merah OFF */
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, GPIO_PIN_RESET); /* Buzzer OFF */
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, GPIO_PIN_RESET); /* LED Alarm OFF */
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_11, GPIO_PIN_RESET); /* Relay OFF */
            HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);   /* Onboard LED OFF */
            Fan_SetSpeed(0);
        }
        else if (csri < 60.0f)
        {
            strcpy(status_msg, "WARNING");
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_15, GPIO_PIN_SET);   /* LED Hijau ON */
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_14, GPIO_PIN_RESET); /* LED Merah OFF */
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, GPIO_PIN_RESET); /* Buzzer OFF */
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, GPIO_PIN_RESET); /* LED Alarm OFF */
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_11, GPIO_PIN_RESET); /* Relay OFF */
            HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET); /* Onboard LED ON */
            Fan_SetSpeed(30);
        }
        else if (csri < 80.0f)
        {
            strcpy(status_msg, "DANGER");
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_15, GPIO_PIN_RESET); /* LED Hijau OFF */
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_14, GPIO_PIN_SET);   /* LED Merah ON */
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, GPIO_PIN_SET);   /* Buzzer ON */
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_11, GPIO_PIN_RESET); /* Relay OFF */
            HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET); /* Onboard LED ON */
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, GPIO_PIN_SET);
            HAL_Delay(100);
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, GPIO_PIN_RESET);
            Fan_SetSpeed(70);
        }
        else
        {
            strcpy(status_msg, "CRITICAL");
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_15, GPIO_PIN_RESET); /* LED Hijau OFF */
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_14, GPIO_PIN_SET);   /* LED Merah ON */
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, GPIO_PIN_SET);   /* Buzzer ON */
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, GPIO_PIN_SET);   /* LED Alarm ON */
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_11, GPIO_PIN_SET);   /* Relay ON */
            HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET); /* Onboard LED ON */
            Fan_SetSpeed(100);
        }

        /* UART kirim data */
        int len = sprintf(uart_buf,
            "TEMP=%.1f HUM=%.1f MOIST=%.1f CO2=%.1f CSRI=%.1f\r\n",
            temperature, humidity, moisture_pct, co2_pct, csri);
        HAL_UART_Transmit(&huart1, (uint8_t*)uart_buf, len, 1000);

        /* LCD update */
        char lcd1[17], lcd2[17];
        sprintf(lcd1, "T:%.1f H:%.0f%%", temperature, humidity);
        sprintf(lcd2, "%-7s C:%.0f", status_msg, csri);

        lcd_put_cur(0, 0);
        lcd_send_string("                ");
        lcd_put_cur(0, 0);
        lcd_send_string(lcd1);

        lcd_put_cur(1, 0);
        lcd_send_string("                ");
        lcd_put_cur(1, 0);
        lcd_send_string(lcd2);

        HAL_Delay(1000);
    }
}

/* System Clock — HSI, tidak butuh crystal eksternal, aman untuk Proteus */
void SystemClock_Config(void)
{
    RCC_OscInitTypeDef RCC_OscInitStruct   = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct   = {0};
    RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

    RCC_OscInitStruct.OscillatorType      = RCC_OSCILLATORTYPE_HSI;
    RCC_OscInitStruct.HSIState            = RCC_HSI_ON;
    RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
    RCC_OscInitStruct.PLL.PLLState        = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource       = RCC_PLLSOURCE_HSI_DIV2;
    RCC_OscInitStruct.PLL.PLLMUL          = RCC_PLL_MUL16;
    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
        Error_Handler();

    RCC_ClkInitStruct.ClockType      = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK
                                     | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource   = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider  = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
    if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
        Error_Handler();

    PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_ADC;
    PeriphClkInit.AdcClockSelection    = RCC_ADCPCLK2_DIV6;
    if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
        Error_Handler();
}

static void MX_ADC1_Init(void)
{
    ADC_ChannelConfTypeDef sConfig = {0};
    hadc1.Instance                 = ADC1;
    hadc1.Init.ScanConvMode        = ADC_SCAN_DISABLE;
    hadc1.Init.ContinuousConvMode  = DISABLE;
    hadc1.Init.DiscontinuousConvMode = DISABLE;
    hadc1.Init.ExternalTrigConv    = ADC_SOFTWARE_START;
    hadc1.Init.DataAlign           = ADC_DATAALIGN_RIGHT;
    hadc1.Init.NbrOfConversion     = 1;
    if (HAL_ADC_Init(&hadc1) != HAL_OK) Error_Handler();

    sConfig.Channel      = ADC_CHANNEL_0;
    sConfig.Rank         = ADC_REGULAR_RANK_1;
    sConfig.SamplingTime = ADC_SAMPLETIME_71CYCLES_5;
    if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK) Error_Handler();
}

static void MX_I2C1_Init(void)
{
    hi2c1.Instance             = I2C1;
    hi2c1.Init.ClockSpeed      = 100000;
    hi2c1.Init.DutyCycle       = I2C_DUTYCYCLE_2;
    hi2c1.Init.OwnAddress1     = 0;
    hi2c1.Init.AddressingMode  = I2C_ADDRESSINGMODE_7BIT;
    hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
    hi2c1.Init.OwnAddress2     = 0;
    hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
    hi2c1.Init.NoStretchMode   = I2C_NOSTRETCH_DISABLE;
    if (HAL_I2C_Init(&hi2c1) != HAL_OK) Error_Handler();
}

static void MX_TIM1_Init(void)
{
    TIM_MasterConfigTypeDef sMasterConfig       = {0};
    TIM_OC_InitTypeDef sConfigOC                = {0};
    TIM_BreakDeadTimeConfigTypeDef sBreakConfig = {0};

    htim1.Instance               = TIM1;
    htim1.Init.Prescaler         = 0;
    htim1.Init.CounterMode       = TIM_COUNTERMODE_UP;
    htim1.Init.Period            = 65535;
    htim1.Init.ClockDivision     = TIM_CLOCKDIVISION_DIV1;
    htim1.Init.RepetitionCounter = 0;
    htim1.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
    if (HAL_TIM_PWM_Init(&htim1) != HAL_OK) Error_Handler();

    sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
    sMasterConfig.MasterSlaveMode     = TIM_MASTERSLAVEMODE_DISABLE;
    if (HAL_TIMEx_MasterConfigSynchronization(&htim1, &sMasterConfig) != HAL_OK)
        Error_Handler();

    sConfigOC.OCMode       = TIM_OCMODE_PWM1;
    sConfigOC.Pulse        = 0;
    sConfigOC.OCPolarity   = TIM_OCPOLARITY_HIGH;
    sConfigOC.OCNPolarity  = TIM_OCNPOLARITY_HIGH;
    sConfigOC.OCFastMode   = TIM_OCFAST_DISABLE;
    sConfigOC.OCIdleState  = TIM_OCIDLESTATE_RESET;
    sConfigOC.OCNIdleState = TIM_OCNIDLESTATE_RESET;
    if (HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_1) != HAL_OK)
        Error_Handler();

    sBreakConfig.OffStateRunMode  = TIM_OSSR_DISABLE;
    sBreakConfig.OffStateIDLEMode = TIM_OSSI_DISABLE;
    sBreakConfig.LockLevel        = TIM_LOCKLEVEL_OFF;
    sBreakConfig.DeadTime         = 0;
    sBreakConfig.BreakState       = TIM_BREAK_DISABLE;
    sBreakConfig.BreakPolarity    = TIM_BREAKPOLARITY_HIGH;
    sBreakConfig.AutomaticOutput  = TIM_AUTOMATICOUTPUT_DISABLE;
    if (HAL_TIMEx_ConfigBreakDeadTime(&htim1, &sBreakConfig) != HAL_OK)
        Error_Handler();

    HAL_TIM_MspPostInit(&htim1);
}

static void MX_TIM2_Init(void)
{
    TIM_MasterConfigTypeDef sMasterConfig = {0};
    TIM_OC_InitTypeDef sConfigOC          = {0};

    htim2.Instance               = TIM2;
    htim2.Init.Prescaler         = 0;
    htim2.Init.CounterMode       = TIM_COUNTERMODE_UP;
    htim2.Init.Period            = 65535;
    htim2.Init.ClockDivision     = TIM_CLOCKDIVISION_DIV1;
    htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
    if (HAL_TIM_PWM_Init(&htim2) != HAL_OK) Error_Handler();

    sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
    sMasterConfig.MasterSlaveMode     = TIM_MASTERSLAVEMODE_DISABLE;
    if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
        Error_Handler();

    sConfigOC.OCMode     = TIM_OCMODE_PWM1;
    sConfigOC.Pulse      = 0;
    sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
    sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
    if (HAL_TIM_PWM_ConfigChannel(&htim2, &sConfigOC, TIM_CHANNEL_3) != HAL_OK)
        Error_Handler();

    HAL_TIM_MspPostInit(&htim2);
}

static void MX_USART1_UART_Init(void)
{
    huart1.Instance          = USART1;
    huart1.Init.BaudRate     = 115200;
    huart1.Init.WordLength   = UART_WORDLENGTH_8B;
    huart1.Init.StopBits     = UART_STOPBITS_1;
    huart1.Init.Parity       = UART_PARITY_NONE;
    huart1.Init.Mode         = UART_MODE_TX_RX;
    huart1.Init.HwFlowCtl    = UART_HWCONTROL_NONE;
    huart1.Init.OverSampling = UART_OVERSAMPLING_16;
    if (HAL_UART_Init(&huart1) != HAL_OK) Error_Handler();
}

static void MX_GPIO_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    __HAL_RCC_GPIOC_CLK_ENABLE();
    __HAL_RCC_GPIOD_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();

    /* Output awal semua LOW */
    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0 | GPIO_PIN_1  | GPIO_PIN_11 |
                              GPIO_PIN_12 | GPIO_PIN_13 | GPIO_PIN_14 |
                              GPIO_PIN_15, GPIO_PIN_RESET);

    /* PC13 — Onboard LED */
    GPIO_InitStruct.Pin   = GPIO_PIN_13;
    GPIO_InitStruct.Mode  = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull  = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

    /* PA2 — PIR input */
    /* PA3 — input cadangan */
    GPIO_InitStruct.Pin  = GPIO_PIN_2 | GPIO_PIN_3;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_PULLDOWN;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    /* PB0  — IN1 L293D (motor) */
    /* PB1  — IN2 L293D (motor) */
    /* PB11 — Relay/Solenoid    */
    /* PB12 — Buzzer            */
    /* PB13 — LED Alarm         */
    /* PB14 — LED Merah         */
    /* PB15 — LED Hijau         */
    GPIO_InitStruct.Pin   = GPIO_PIN_0  | GPIO_PIN_1  | GPIO_PIN_11 |
                            GPIO_PIN_12 | GPIO_PIN_13 | GPIO_PIN_14 |
                            GPIO_PIN_15;
    GPIO_InitStruct.Mode  = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull  = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
}

void Error_Handler(void)
{
    __disable_irq();
    while (1) {}
}