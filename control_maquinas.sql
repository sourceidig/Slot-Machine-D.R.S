-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 24-11-2025 a las 21:52:05
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `control_maquinas`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cierre_turno`
--

CREATE TABLE `cierre_turno` (
  `id_cierre` int(11) NOT NULL,
  `id_sucursal` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `turno` enum('Mañana','Tarde','Noche') NOT NULL,
  `encargado_id` int(11) NOT NULL,
  `estado` enum('Abierto','Cerrado','Aprobado') NOT NULL DEFAULT 'Abierto',
  `observaciones` text DEFAULT NULL,
  `total_zona` decimal(14,2) DEFAULT NULL,
  `total_cierre` decimal(14,2) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `cierre_turno`
--

INSERT INTO `cierre_turno` (`id_cierre`, `id_sucursal`, `fecha`, `turno`, `encargado_id`, `estado`, `observaciones`, `total_zona`, `total_cierre`, `created_by`, `created_at`) VALUES
(1, 2, '2025-11-20', 'Noche', 2, 'Cerrado', 'Turno generado por Faker para pruebas.', 109659.00, 109659.00, 2, '2025-11-24 20:51:03'),
(2, 3, '2025-11-14', 'Mañana', 4, 'Cerrado', 'Turno generado por Faker para pruebas.', 898192.00, 898192.00, 4, '2025-11-24 20:51:03'),
(3, 1, '2025-11-15', 'Noche', 4, 'Cerrado', 'Turno generado por Faker para pruebas.', 203262.00, 203262.00, 4, '2025-11-24 20:51:03'),
(4, 2, '2025-11-16', 'Noche', 4, 'Cerrado', 'Turno generado por Faker para pruebas.', 281037.00, 281037.00, 4, '2025-11-24 20:51:03'),
(5, 2, '2025-11-23', 'Noche', 5, 'Cerrado', 'Turno generado por Faker para pruebas.', 289660.00, 289660.00, 5, '2025-11-24 20:51:03'),
(6, 1, '2025-11-22', 'Tarde', 3, 'Cerrado', 'Turno generado por Faker para pruebas.', 423624.00, 423624.00, 3, '2025-11-24 20:51:03'),
(7, 2, '2025-11-10', 'Mañana', 4, 'Cerrado', 'Turno generado por Faker para pruebas.', 258406.00, 258406.00, 4, '2025-11-24 20:51:03'),
(8, 2, '2025-11-23', 'Tarde', 4, 'Cerrado', 'Turno generado por Faker para pruebas.', 858117.00, 858117.00, 4, '2025-11-24 20:51:03'),
(9, 1, '2025-11-10', 'Tarde', 2, 'Cerrado', 'Turno generado por Faker para pruebas.', 116793.00, 116793.00, 2, '2025-11-24 20:51:03'),
(10, 3, '2025-11-13', 'Noche', 5, 'Cerrado', 'Turno generado por Faker para pruebas.', 515192.00, 515192.00, 5, '2025-11-24 20:51:03'),
(11, 1, '2025-11-13', 'Mañana', 5, 'Cerrado', 'Turno generado por Faker para pruebas.', 751253.00, 751253.00, 5, '2025-11-24 20:51:03'),
(12, 3, '2025-11-17', 'Tarde', 4, 'Cerrado', 'Turno generado por Faker para pruebas.', 731377.00, 731377.00, 4, '2025-11-24 20:51:03'),
(13, 1, '2025-11-19', 'Mañana', 5, 'Cerrado', 'Turno generado por Faker para pruebas.', 866922.00, 866922.00, 5, '2025-11-24 20:51:03'),
(14, 2, '2025-11-21', 'Noche', 2, 'Cerrado', 'Turno generado por Faker para pruebas.', 286566.00, 286566.00, 2, '2025-11-24 20:51:03'),
(15, 3, '2025-11-19', 'Noche', 3, 'Cerrado', 'Turno generado por Faker para pruebas.', 1039694.00, 1039694.00, 3, '2025-11-24 20:51:04'),
(16, 2, '2025-11-19', 'Tarde', 2, 'Cerrado', 'Turno generado por Faker para pruebas.', 153996.00, 153996.00, 2, '2025-11-24 20:51:04'),
(17, 1, '2025-11-20', 'Mañana', 5, 'Cerrado', 'Turno generado por Faker para pruebas.', 248414.00, 248414.00, 5, '2025-11-24 20:51:04'),
(18, 2, '2025-11-17', 'Tarde', 3, 'Cerrado', 'Turno generado por Faker para pruebas.', 797669.00, 797669.00, 3, '2025-11-24 20:51:04'),
(19, 2, '2025-11-21', 'Tarde', 2, 'Cerrado', 'Turno generado por Faker para pruebas.', 205299.00, 205299.00, 2, '2025-11-24 20:51:04'),
(20, 3, '2025-11-11', 'Mañana', 2, 'Cerrado', 'Turno generado por Faker para pruebas.', 1046858.00, 1046858.00, 2, '2025-11-24 20:51:04'),
(21, 3, '2025-11-11', 'Tarde', 4, 'Cerrado', 'Turno generado por Faker para pruebas.', 769680.00, 769680.00, 4, '2025-11-24 20:51:04'),
(22, 3, '2025-11-15', 'Mañana', 4, 'Cerrado', 'Turno generado por Faker para pruebas.', 356130.00, 356130.00, 4, '2025-11-24 20:51:04'),
(23, 2, '2025-11-20', 'Mañana', 5, 'Cerrado', 'Turno generado por Faker para pruebas.', 692073.00, 692073.00, 5, '2025-11-24 20:51:04'),
(24, 2, '2025-11-21', 'Noche', 5, 'Cerrado', 'Turno generado por Faker para pruebas.', 456887.00, 456887.00, 5, '2025-11-24 20:51:04'),
(25, 2, '2025-11-17', 'Noche', 3, 'Cerrado', 'Turno generado por Faker para pruebas.', 621157.00, 621157.00, 3, '2025-11-24 20:51:04'),
(26, 1, '2025-11-15', 'Mañana', 5, 'Cerrado', 'Turno generado por Faker para pruebas.', 576949.00, 576949.00, 5, '2025-11-24 20:51:04'),
(27, 2, '2025-11-22', 'Noche', 4, 'Cerrado', 'Turno generado por Faker para pruebas.', 697299.00, 697299.00, 4, '2025-11-24 20:51:04'),
(28, 2, '2025-11-13', 'Tarde', 3, 'Cerrado', 'Turno generado por Faker para pruebas.', 149108.00, 149108.00, 3, '2025-11-24 20:51:04'),
(29, 1, '2025-11-15', 'Tarde', 3, 'Cerrado', 'Turno generado por Faker para pruebas.', 291341.00, 291341.00, 3, '2025-11-24 20:51:05'),
(30, 2, '2025-11-17', 'Mañana', 3, 'Cerrado', 'Turno generado por Faker para pruebas.', 350726.00, 350726.00, 3, '2025-11-24 20:51:05'),
(31, 2, '2025-11-15', 'Noche', 2, 'Cerrado', 'Turno generado por Faker para pruebas.', 418148.00, 418148.00, 2, '2025-11-24 20:51:05'),
(32, 3, '2025-11-23', 'Noche', 4, 'Cerrado', 'Turno generado por Faker para pruebas.', 606852.00, 606852.00, 4, '2025-11-24 20:51:05'),
(33, 1, '2025-11-17', 'Noche', 5, 'Cerrado', 'Turno generado por Faker para pruebas.', 391180.00, 391180.00, 5, '2025-11-24 20:51:05'),
(34, 1, '2025-11-22', 'Mañana', 2, 'Cerrado', 'Turno generado por Faker para pruebas.', 825556.00, 825556.00, 2, '2025-11-24 20:51:05'),
(35, 2, '2025-11-22', 'Mañana', 4, 'Cerrado', 'Turno generado por Faker para pruebas.', 251363.00, 251363.00, 4, '2025-11-24 20:51:05'),
(36, 3, '2025-11-22', 'Noche', 4, 'Cerrado', 'Turno generado por Faker para pruebas.', 280597.00, 280597.00, 4, '2025-11-24 20:51:05'),
(37, 1, '2025-11-11', 'Mañana', 2, 'Cerrado', 'Turno generado por Faker para pruebas.', 301548.00, 301548.00, 2, '2025-11-24 20:51:05'),
(38, 1, '2025-11-12', 'Noche', 5, 'Cerrado', 'Turno generado por Faker para pruebas.', 315676.00, 315676.00, 5, '2025-11-24 20:51:05'),
(39, 3, '2025-11-22', 'Tarde', 2, 'Cerrado', 'Turno generado por Faker para pruebas.', 847960.00, 847960.00, 2, '2025-11-24 20:51:05'),
(40, 1, '2025-11-17', 'Mañana', 2, 'Cerrado', 'Turno generado por Faker para pruebas.', 791889.00, 791889.00, 2, '2025-11-24 20:51:05'),
(41, 3, '2025-11-22', 'Noche', 4, 'Cerrado', 'Turno generado por Faker para pruebas.', 793273.00, 793273.00, 4, '2025-11-24 20:51:05'),
(42, 2, '2025-11-16', 'Noche', 4, 'Cerrado', 'Turno generado por Faker para pruebas.', 697164.00, 697164.00, 4, '2025-11-24 20:51:05'),
(43, 2, '2025-11-17', 'Mañana', 2, 'Cerrado', 'Turno generado por Faker para pruebas.', 840002.00, 840002.00, 2, '2025-11-24 20:51:05'),
(44, 2, '2025-11-14', 'Noche', 2, 'Cerrado', 'Turno generado por Faker para pruebas.', 961326.00, 961326.00, 2, '2025-11-24 20:51:05'),
(45, 2, '2025-11-18', 'Mañana', 2, 'Cerrado', 'Turno generado por Faker para pruebas.', 925292.00, 925292.00, 2, '2025-11-24 20:51:05'),
(46, 2, '2025-11-10', 'Mañana', 3, 'Cerrado', 'Turno generado por Faker para pruebas.', 448349.00, 448349.00, 3, '2025-11-24 20:51:06'),
(47, 1, '2025-11-22', 'Noche', 3, 'Cerrado', 'Turno generado por Faker para pruebas.', 505154.00, 505154.00, 3, '2025-11-24 20:51:06'),
(48, 1, '2025-11-15', 'Mañana', 5, 'Cerrado', 'Turno generado por Faker para pruebas.', 255122.00, 255122.00, 5, '2025-11-24 20:51:06'),
(49, 3, '2025-11-23', 'Noche', 3, 'Cerrado', 'Turno generado por Faker para pruebas.', 310574.00, 310574.00, 3, '2025-11-24 20:51:06'),
(50, 1, '2025-11-23', 'Mañana', 3, 'Cerrado', 'Turno generado por Faker para pruebas.', 173107.00, 173107.00, 3, '2025-11-24 20:51:06'),
(51, 3, '2025-11-12', 'Noche', 3, 'Cerrado', 'Turno generado por Faker para pruebas.', 199637.00, 199637.00, 3, '2025-11-24 20:51:06'),
(52, 1, '2025-11-11', 'Noche', 3, 'Cerrado', 'Turno generado por Faker para pruebas.', 435762.00, 435762.00, 3, '2025-11-24 20:51:06'),
(53, 3, '2025-11-14', 'Mañana', 5, 'Cerrado', 'Turno generado por Faker para pruebas.', 364904.00, 364904.00, 5, '2025-11-24 20:51:06'),
(54, 2, '2025-11-16', 'Tarde', 5, 'Cerrado', 'Turno generado por Faker para pruebas.', 1863.00, 1863.00, 5, '2025-11-24 20:51:06');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `lectura_maquina`
--

CREATE TABLE `lectura_maquina` (
  `id_lectura` int(11) NOT NULL,
  `id_cierre` int(11) NOT NULL,
  `id_maquina` int(11) NOT NULL,
  `id_zona` int(11) NOT NULL,
  `numero_maquina` smallint(6) NOT NULL,
  `nombre_persona` varchar(150) DEFAULT NULL,
  `caja` decimal(14,2) DEFAULT NULL,
  `numeral` decimal(14,2) DEFAULT NULL,
  `prestamos` decimal(14,2) DEFAULT NULL,
  `redbank` decimal(14,2) DEFAULT NULL,
  `retiros` decimal(14,2) DEFAULT NULL,
  `total_caja` decimal(14,2) DEFAULT NULL,
  `billete_20000` int(11) DEFAULT NULL,
  `billete_10000` int(11) DEFAULT NULL,
  `billete_5000` int(11) DEFAULT NULL,
  `billete_2000` int(11) DEFAULT NULL,
  `billete_1000` int(11) DEFAULT NULL,
  `monedas_total` decimal(14,2) DEFAULT NULL,
  `total_entregado` decimal(14,2) DEFAULT NULL,
  `descuadre` decimal(14,2) DEFAULT NULL,
  `nota` text DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `lectura_maquina`
--

INSERT INTO `lectura_maquina` (`id_lectura`, `id_cierre`, `id_maquina`, `id_zona`, `numero_maquina`, `nombre_persona`, `caja`, `numeral`, `prestamos`, `redbank`, `retiros`, `total_caja`, `billete_20000`, `billete_10000`, `billete_5000`, `billete_2000`, `billete_1000`, `monedas_total`, `total_entregado`, `descuadre`, `nota`, `created_by`, `created_at`) VALUES
(1, 1, 22, 5, 22, 'Darío Nevado Bernad', 61421.00, 61421.00, 0.00, 0.00, 42019.00, 19402.00, 5, 4, 4, 3, 2, 1205.00, 169205.00, -149803.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:03'),
(2, 1, 22, 5, 22, 'Macarena Carballo Coloma', 192981.00, 192981.00, 0.00, 0.00, 163059.00, 29922.00, 2, 2, 8, 1, 9, 5178.00, 116178.00, -86256.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:03'),
(3, 1, 21, 5, 21, 'Eleuterio Juan Giner', 26516.00, 26516.00, 0.00, 0.00, 8057.00, 18459.00, 5, 3, 5, 10, 7, 17855.00, 199855.00, -181396.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:03'),
(4, 1, 25, 5, 25, 'Clotilde Redondo Pedrero', 78673.00, 78673.00, 0.00, 0.00, 65736.00, 12937.00, 0, 3, 6, 5, 3, 17163.00, 90163.00, -77226.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:03'),
(5, 1, 21, 5, 21, 'Ximena Jerez-Madrid', 7401.00, 7401.00, 0.00, 0.00, 1069.00, 6332.00, 0, 9, 10, 0, 16, 7198.00, 163198.00, -156866.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:03'),
(6, 1, 24, 5, 24, 'Jose Angel Sergio Amat Cortina', 42963.00, 42963.00, 0.00, 0.00, 20356.00, 22607.00, 0, 4, 4, 10, 10, 8860.00, 98860.00, -76253.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:03'),
(7, 2, 37, 8, 37, 'Leocadio Iborra', 90628.00, 90628.00, 0.00, 0.00, 49294.00, 41334.00, 3, 0, 1, 9, 11, 12784.00, 106784.00, -65450.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(8, 2, 38, 8, 38, 'Noemí del Ferrándiz', 197771.00, 197771.00, 0.00, 0.00, 19505.00, 178266.00, 5, 0, 4, 8, 7, 876.00, 143876.00, 34390.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(9, 2, 36, 8, 36, 'Renata Neira', 197134.00, 197134.00, 0.00, 0.00, 21407.00, 175727.00, 3, 2, 2, 4, 6, 8100.00, 112100.00, 63627.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(10, 2, 39, 8, 39, 'Gonzalo Peral Alemany', 68828.00, 68828.00, 0.00, 0.00, 25642.00, 43186.00, 2, 5, 4, 0, 0, 14521.00, 124521.00, -81335.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(11, 2, 37, 8, 37, 'Alfredo del Jaume', 196287.00, 196287.00, 0.00, 0.00, 45039.00, 151248.00, 5, 2, 2, 6, 2, 385.00, 144385.00, 6863.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(12, 2, 40, 8, 40, 'Belén Custodia Plana Sedano', 60537.00, 60537.00, 0.00, 0.00, 55128.00, 5409.00, 3, 7, 6, 7, 15, 10664.00, 199664.00, -194255.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(13, 2, 39, 8, 39, 'Ruth del Valdés', 73985.00, 73985.00, 0.00, 0.00, 24073.00, 49912.00, 2, 3, 5, 3, 16, 17482.00, 134482.00, -84570.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(14, 2, 36, 8, 36, 'Olivia Grau Uría', 198722.00, 198722.00, 0.00, 0.00, 28534.00, 170188.00, 0, 5, 0, 3, 4, 16826.00, 76826.00, 93362.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(15, 2, 37, 8, 37, 'Visitación Llanos Macías', 139529.00, 139529.00, 0.00, 0.00, 56607.00, 82922.00, 3, 10, 7, 4, 8, 1024.00, 212024.00, -129102.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(16, 3, 15, 3, 15, 'Esteban Roselló Sáez', 160131.00, 160131.00, 0.00, 0.00, 25720.00, 134411.00, 0, 8, 6, 8, 1, 7692.00, 134692.00, -281.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(17, 3, 13, 3, 13, 'Clemente Ramírez Maestre', 38017.00, 38017.00, 0.00, 0.00, 24289.00, 13728.00, 2, 1, 8, 2, 7, 14936.00, 115936.00, -102208.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(18, 3, 11, 3, 11, 'Fabián Ballester', 58184.00, 58184.00, 0.00, 0.00, 32718.00, 25466.00, 2, 4, 4, 7, 5, 9456.00, 128456.00, -102990.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(19, 3, 12, 3, 12, 'Ainoa Ordóñez-Quintanilla', 29157.00, 29157.00, 0.00, 0.00, 11060.00, 18097.00, 4, 3, 8, 4, 5, 14367.00, 177367.00, -159270.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(20, 3, 14, 3, 14, 'Amaya Uribe Múñiz', 88307.00, 88307.00, 0.00, 0.00, 87403.00, 904.00, 3, 2, 8, 6, 3, 6079.00, 141079.00, -140175.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(21, 3, 11, 3, 11, 'Anabel Fortuny Manuel', 24177.00, 24177.00, 0.00, 0.00, 13521.00, 10656.00, 1, 0, 0, 2, 8, 4952.00, 36952.00, -26296.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(22, 4, 23, 5, 23, 'Micaela Peñas Jerez', 24200.00, 24200.00, 0.00, 0.00, 608.00, 23592.00, 3, 4, 7, 2, 9, 802.00, 148802.00, -125210.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(23, 4, 21, 5, 21, 'Mauricio Ayllón Olmo', 162142.00, 162142.00, 0.00, 0.00, 154310.00, 7832.00, 3, 10, 7, 5, 11, 9234.00, 225234.00, -217402.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(24, 4, 22, 5, 22, 'Cayetano Agustín Lobato Saldaña', 182283.00, 182283.00, 0.00, 0.00, 19397.00, 162886.00, 3, 2, 3, 9, 17, 6911.00, 136911.00, 25975.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(25, 4, 23, 5, 23, 'Luz Arnal Sáez', 51873.00, 51873.00, 0.00, 0.00, 35484.00, 16389.00, 4, 8, 1, 4, 8, 2875.00, 183875.00, -167486.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(26, 4, 22, 5, 22, 'Cruz Tamayo-Echevarría', 192875.00, 192875.00, 0.00, 0.00, 147919.00, 44956.00, 3, 7, 10, 6, 19, 9737.00, 220737.00, -175781.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(27, 4, 25, 5, 25, 'Pedro Pascual Sarmiento Valera', 45124.00, 45124.00, 0.00, 0.00, 19742.00, 25382.00, 0, 0, 7, 6, 15, 7993.00, 69993.00, -44611.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(28, 5, 27, 6, 27, 'Albina Amaya Dominguez', 151714.00, 151714.00, 0.00, 0.00, 58058.00, 93656.00, 1, 10, 7, 4, 7, 17002.00, 187002.00, -93346.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(29, 5, 28, 6, 28, 'Curro Prats', 60985.00, 60985.00, 0.00, 0.00, 52605.00, 8380.00, 4, 6, 1, 1, 12, 13797.00, 172797.00, -164417.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(30, 5, 27, 6, 27, 'Fabio del Mateu', 68871.00, 68871.00, 0.00, 0.00, 10762.00, 58109.00, 4, 4, 6, 4, 16, 15863.00, 189863.00, -131754.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(31, 5, 28, 6, 28, 'Manu Ribera-Castellanos', 53522.00, 53522.00, 0.00, 0.00, 25493.00, 28029.00, 1, 2, 4, 10, 18, 16082.00, 114082.00, -86053.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(32, 5, 30, 6, 30, 'Anselma Diez Camino', 98769.00, 98769.00, 0.00, 0.00, 62482.00, 36287.00, 1, 10, 10, 1, 16, 6942.00, 194942.00, -158655.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(33, 5, 30, 6, 30, 'Maximiliano Casal', 84381.00, 84381.00, 0.00, 0.00, 75339.00, 9042.00, 2, 8, 10, 7, 19, 12872.00, 215872.00, -206830.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(34, 5, 29, 6, 29, 'Alexandra Maestre Romero', 41396.00, 41396.00, 0.00, 0.00, 10420.00, 30976.00, 5, 4, 9, 8, 6, 14099.00, 221099.00, -190123.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(35, 5, 27, 6, 27, 'Abraham Malo Robles', 145986.00, 145986.00, 0.00, 0.00, 120805.00, 25181.00, 0, 4, 10, 1, 8, 17027.00, 117027.00, -91846.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(36, 6, 8, 2, 8, 'Cándida Corral-Gomila', 187132.00, 187132.00, 0.00, 0.00, 27687.00, 159445.00, 3, 8, 0, 5, 0, 2999.00, 152999.00, 6446.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:03'),
(37, 6, 10, 2, 10, 'Roberto Aller Roda', 172172.00, 172172.00, 0.00, 0.00, 94369.00, 77803.00, 0, 4, 5, 9, 11, 18193.00, 112193.00, -34390.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:03'),
(38, 6, 10, 2, 10, 'Teodosio Fuente Borrego', 134544.00, 134544.00, 0.00, 0.00, 90460.00, 44084.00, 3, 10, 1, 5, 13, 7695.00, 195695.00, -151611.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:03'),
(39, 6, 9, 2, 9, 'Ofelia Ema Trillo Nicolás', 19043.00, 19043.00, 0.00, 0.00, 17381.00, 1662.00, 3, 8, 0, 10, 18, 9936.00, 187936.00, -186274.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:03'),
(40, 6, 7, 2, 7, 'Felipe de Sacristán', 83521.00, 83521.00, 0.00, 0.00, 65019.00, 18502.00, 1, 5, 4, 4, 18, 13831.00, 129831.00, -111329.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:03'),
(41, 6, 7, 2, 7, 'Custodia Alcázar Cárdenas', 35701.00, 35701.00, 0.00, 0.00, 35693.00, 8.00, 2, 3, 3, 1, 4, 2328.00, 93328.00, -93320.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:03'),
(42, 6, 9, 2, 9, 'Dolores Garrido Lerma', 90557.00, 90557.00, 0.00, 0.00, 16738.00, 73819.00, 2, 8, 7, 3, 10, 3419.00, 174419.00, -100600.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:03'),
(43, 6, 7, 2, 7, 'Eligio Godoy-Bonet', 193392.00, 193392.00, 0.00, 0.00, 145091.00, 48301.00, 5, 9, 9, 5, 11, 15966.00, 271966.00, -223665.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:03'),
(44, 7, 24, 5, 24, 'Juan Pablo Molina', 75071.00, 75071.00, 0.00, 0.00, 49545.00, 25526.00, 3, 2, 2, 0, 4, 19524.00, 113524.00, -87998.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(45, 7, 24, 5, 24, 'Felipe Vázquez Uriarte', 182614.00, 182614.00, 0.00, 0.00, 8913.00, 173701.00, 3, 8, 6, 10, 13, 13518.00, 216518.00, -42817.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(46, 7, 23, 5, 23, 'Toni Herrero Bonet', 157293.00, 157293.00, 0.00, 0.00, 112612.00, 44681.00, 5, 2, 10, 7, 8, 19505.00, 211505.00, -166824.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(47, 7, 22, 5, 22, 'Felix Gallardo', 16948.00, 16948.00, 0.00, 0.00, 7932.00, 9016.00, 1, 2, 5, 0, 11, 13404.00, 89404.00, -80388.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(48, 7, 24, 5, 24, 'Eliseo Vázquez Bauzà', 31936.00, 31936.00, 0.00, 0.00, 26454.00, 5482.00, 2, 10, 6, 9, 4, 15362.00, 207362.00, -201880.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(49, 8, 30, 6, 30, 'Maximino Aragonés-Tirado', 98538.00, 98538.00, 0.00, 0.00, 14009.00, 84529.00, 2, 9, 4, 6, 11, 4897.00, 177897.00, -93368.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(50, 8, 28, 6, 28, 'Teo Codina', 114145.00, 114145.00, 0.00, 0.00, 9151.00, 104994.00, 4, 9, 5, 0, 12, 5211.00, 212211.00, -107217.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(51, 8, 26, 6, 26, 'Bonifacio Dominguez', 39511.00, 39511.00, 0.00, 0.00, 158.00, 39353.00, 5, 8, 6, 8, 1, 5006.00, 232006.00, -192653.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(52, 8, 29, 6, 29, 'Virgilio Rivero', 35603.00, 35603.00, 0.00, 0.00, 31696.00, 3907.00, 3, 7, 10, 1, 18, 14462.00, 214462.00, -210555.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(53, 8, 30, 6, 30, 'Olivia Taboada Gutiérrez', 66654.00, 66654.00, 0.00, 0.00, 53443.00, 13211.00, 4, 9, 3, 3, 16, 6054.00, 213054.00, -199843.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(54, 8, 30, 6, 30, 'Angelino Jordán-Leiva', 149748.00, 149748.00, 0.00, 0.00, 33227.00, 116521.00, 0, 6, 9, 3, 15, 9809.00, 135809.00, -19288.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(55, 8, 28, 6, 28, 'Fátima Dominga Nevado Nebot', 183782.00, 183782.00, 0.00, 0.00, 71747.00, 112035.00, 2, 6, 4, 6, 13, 5389.00, 150389.00, -38354.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(56, 8, 29, 6, 29, 'Josué Mendizábal Parejo', 103226.00, 103226.00, 0.00, 0.00, 40578.00, 62648.00, 2, 1, 10, 3, 17, 6322.00, 129322.00, -66674.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(57, 8, 27, 6, 27, 'Valero Ríos Abellán', 120352.00, 120352.00, 0.00, 0.00, 95793.00, 24559.00, 1, 4, 1, 3, 5, 18213.00, 94213.00, -69654.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(58, 8, 29, 6, 29, 'Gracia Gras Pardo', 46520.00, 46520.00, 0.00, 0.00, 36565.00, 9955.00, 2, 8, 5, 1, 7, 5060.00, 159060.00, -149105.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(59, 8, 30, 6, 30, 'Jimena Cortés Escalona', 196700.00, 196700.00, 0.00, 0.00, 71143.00, 125557.00, 3, 3, 4, 7, 14, 8676.00, 146676.00, -21119.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(60, 8, 29, 6, 29, 'Arturo Menendez Saura', 77054.00, 77054.00, 0.00, 0.00, 19593.00, 57461.00, 0, 2, 10, 1, 18, 5670.00, 95670.00, -38209.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(61, 8, 26, 6, 26, 'Natalio Franch Pera', 83189.00, 83189.00, 0.00, 0.00, 30377.00, 52812.00, 2, 2, 4, 4, 0, 18268.00, 106268.00, -53456.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(62, 8, 30, 6, 30, 'Fernanda Vallés Cuesta', 88265.00, 88265.00, 0.00, 0.00, 51824.00, 36441.00, 0, 8, 0, 2, 8, 7320.00, 99320.00, -62879.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(63, 8, 29, 6, 29, 'Teodosio Castillo Otero', 45018.00, 45018.00, 0.00, 0.00, 30884.00, 14134.00, 1, 8, 0, 10, 12, 1775.00, 133775.00, -119641.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(64, 9, 8, 2, 8, 'Angelino Segarra Salamanca', 28281.00, 28281.00, 0.00, 0.00, 19332.00, 8949.00, 5, 10, 6, 4, 5, 5237.00, 248237.00, -239288.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:03'),
(65, 9, 9, 2, 9, 'Maura del Porcel', 96663.00, 96663.00, 0.00, 0.00, 23859.00, 72804.00, 2, 6, 0, 9, 18, 1604.00, 137604.00, -64800.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:03'),
(66, 9, 7, 2, 7, 'Cándida Maricela Cervantes Manuel', 107035.00, 107035.00, 0.00, 0.00, 88575.00, 18460.00, 0, 5, 4, 10, 14, 13754.00, 117754.00, -99294.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:03'),
(67, 9, 10, 2, 10, 'Simón Marciano Pastor Pol', 9681.00, 9681.00, 0.00, 0.00, 1656.00, 8025.00, 3, 5, 4, 6, 0, 2837.00, 144837.00, -136812.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:03'),
(68, 9, 10, 2, 10, 'Pancho Jurado Antón', 27819.00, 27819.00, 0.00, 0.00, 19264.00, 8555.00, 2, 7, 6, 9, 5, 8089.00, 171089.00, -162534.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:03'),
(69, 10, 40, 8, 40, 'Dorita Andres Acedo', 31242.00, 31242.00, 0.00, 0.00, 5612.00, 25630.00, 4, 1, 7, 8, 18, 14934.00, 173934.00, -148304.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(70, 10, 40, 8, 40, 'Mónica Saez Carballo', 142010.00, 142010.00, 0.00, 0.00, 123064.00, 18946.00, 4, 6, 3, 10, 3, 13600.00, 191600.00, -172654.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(71, 10, 36, 8, 36, 'Olegario Severo Abella Vigil', 193685.00, 193685.00, 0.00, 0.00, 104499.00, 89186.00, 4, 0, 3, 1, 4, 14342.00, 115342.00, -26156.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(72, 10, 37, 8, 37, 'Ovidio Gelabert-Julián', 183110.00, 183110.00, 0.00, 0.00, 68717.00, 114393.00, 0, 10, 5, 6, 13, 11191.00, 161191.00, -46798.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(73, 10, 36, 8, 36, 'Elías Antón-Alcántara', 186924.00, 186924.00, 0.00, 0.00, 141778.00, 45146.00, 5, 6, 7, 5, 4, 9563.00, 218563.00, -173417.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(74, 10, 39, 8, 39, 'Pánfilo Mendez Zamorano', 178198.00, 178198.00, 0.00, 0.00, 21026.00, 157172.00, 0, 10, 3, 5, 14, 3323.00, 142323.00, 14849.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(75, 10, 37, 8, 37, 'Ruy Palacios Almazán', 113649.00, 113649.00, 0.00, 0.00, 48937.00, 64712.00, 2, 7, 10, 1, 14, 16990.00, 192990.00, -128278.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(76, 10, 40, 8, 40, 'Fabio Folch Hoyos', 11504.00, 11504.00, 0.00, 0.00, 11497.00, 7.00, 3, 9, 4, 9, 1, 10740.00, 199740.00, -199733.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(77, 11, 6, 2, 6, 'Calisto Laguna Montalbán', 169483.00, 169483.00, 0.00, 0.00, 93427.00, 76056.00, 1, 7, 2, 10, 9, 17499.00, 146499.00, -70443.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(78, 11, 10, 2, 10, 'Leandro Tomé Macias', 28769.00, 28769.00, 0.00, 0.00, 20823.00, 7946.00, 5, 0, 4, 0, 2, 16810.00, 138810.00, -130864.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(79, 11, 6, 2, 6, 'Ramona Bayona Villaverde', 167590.00, 167590.00, 0.00, 0.00, 4509.00, 163081.00, 0, 6, 7, 3, 16, 19029.00, 136029.00, 27052.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(80, 11, 9, 2, 9, 'Cirino Aller Cobo', 86668.00, 86668.00, 0.00, 0.00, 66185.00, 20483.00, 0, 5, 0, 8, 10, 18654.00, 94654.00, -74171.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(81, 11, 7, 2, 7, 'Ruperta del Solís', 173302.00, 173302.00, 0.00, 0.00, 138713.00, 34589.00, 5, 7, 3, 9, 5, 17575.00, 225575.00, -190986.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(82, 11, 6, 2, 6, 'Artemio Blas Galindo López', 152310.00, 152310.00, 0.00, 0.00, 45682.00, 106628.00, 4, 1, 5, 8, 6, 4997.00, 141997.00, -35369.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(83, 11, 8, 2, 8, 'Ezequiel Montes Almansa', 86512.00, 86512.00, 0.00, 0.00, 70105.00, 16407.00, 5, 9, 5, 5, 11, 16499.00, 252499.00, -236092.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(84, 11, 10, 2, 10, 'Regina de Roselló', 87078.00, 87078.00, 0.00, 0.00, 9187.00, 77891.00, 3, 2, 8, 4, 0, 884.00, 128884.00, -50993.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(85, 11, 6, 2, 6, 'Anastasia del Ferrer', 134574.00, 134574.00, 0.00, 0.00, 132944.00, 1630.00, 1, 2, 2, 6, 13, 176.00, 75176.00, -73546.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(86, 11, 9, 2, 9, 'Silvestre Seco Espejo', 186063.00, 186063.00, 0.00, 0.00, 94077.00, 91986.00, 4, 7, 4, 10, 5, 6352.00, 201352.00, -109366.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(87, 11, 10, 2, 10, 'Fabián Blanes Bello', 173213.00, 173213.00, 0.00, 0.00, 18657.00, 154556.00, 0, 6, 8, 4, 12, 14979.00, 134979.00, 19577.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(88, 12, 45, 9, 45, 'Bienvenida del Llopis', 32540.00, 32540.00, 0.00, 0.00, 17416.00, 15124.00, 5, 6, 3, 5, 17, 16218.00, 218218.00, -203094.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(89, 12, 45, 9, 45, 'Gregorio Gordillo Portillo', 195647.00, 195647.00, 0.00, 0.00, 61454.00, 134193.00, 3, 2, 3, 6, 11, 5737.00, 123737.00, 10456.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(90, 12, 45, 9, 45, 'Roberto Montero Río', 131386.00, 131386.00, 0.00, 0.00, 85340.00, 46046.00, 3, 6, 4, 4, 15, 13483.00, 176483.00, -130437.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(91, 12, 41, 9, 41, 'Teresita del Cuesta', 132660.00, 132660.00, 0.00, 0.00, 19586.00, 113074.00, 4, 2, 7, 7, 6, 18532.00, 173532.00, -60458.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(92, 12, 44, 9, 44, 'Gilberto Colomer', 56469.00, 56469.00, 0.00, 0.00, 25109.00, 31360.00, 0, 5, 7, 3, 5, 7374.00, 103374.00, -72014.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(93, 12, 43, 9, 43, 'Claudia Manrique Montesinos', 53627.00, 53627.00, 0.00, 0.00, 18764.00, 34863.00, 5, 0, 4, 3, 8, 19345.00, 153345.00, -118482.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(94, 12, 44, 9, 44, 'Jimena Quintana Salgado', 75517.00, 75517.00, 0.00, 0.00, 21473.00, 54044.00, 4, 4, 5, 5, 12, 17721.00, 184721.00, -130677.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(95, 12, 41, 9, 41, 'Omar Salgado Arroyo', 143420.00, 143420.00, 0.00, 0.00, 64836.00, 78584.00, 4, 8, 9, 6, 11, 11556.00, 239556.00, -160972.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(96, 12, 45, 9, 45, 'Elvira del Calvo', 116820.00, 116820.00, 0.00, 0.00, 73294.00, 43526.00, 1, 7, 1, 2, 4, 13521.00, 116521.00, -72995.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(97, 12, 42, 9, 42, 'Isaac Colomer Royo', 32912.00, 32912.00, 0.00, 0.00, 25065.00, 7847.00, 3, 0, 5, 1, 2, 4042.00, 93042.00, -85195.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(98, 12, 45, 9, 45, 'Dorotea Pons Torrecilla', 178507.00, 178507.00, 0.00, 0.00, 5791.00, 172716.00, 1, 10, 2, 5, 16, 13555.00, 169555.00, 3161.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:03'),
(99, 13, 8, 2, 8, 'Quique Clímaco Blázquez Cazorla', 6955.00, 6955.00, 0.00, 0.00, 3861.00, 3094.00, 4, 4, 8, 5, 19, 2900.00, 191900.00, -188806.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(100, 13, 10, 2, 10, 'Rómulo Jose Rosales Puente', 187367.00, 187367.00, 0.00, 0.00, 27814.00, 159553.00, 0, 7, 7, 4, 0, 17900.00, 130900.00, 28653.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(101, 13, 9, 2, 9, 'Benigno Montenegro Solera', 113824.00, 113824.00, 0.00, 0.00, 73232.00, 40592.00, 3, 2, 1, 10, 1, 18576.00, 124576.00, -83984.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(102, 13, 8, 2, 8, 'Ana Sofía Guzmán Espada', 90019.00, 90019.00, 0.00, 0.00, 25635.00, 64384.00, 4, 5, 2, 4, 10, 1981.00, 159981.00, -95597.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(103, 13, 7, 2, 7, 'Gloria Batalla Gonzalo', 163224.00, 163224.00, 0.00, 0.00, 135226.00, 27998.00, 3, 4, 7, 5, 15, 14504.00, 174504.00, -146506.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(104, 13, 10, 2, 10, 'Heriberto Puerta Heredia', 46059.00, 46059.00, 0.00, 0.00, 45222.00, 837.00, 5, 2, 7, 4, 19, 17494.00, 199494.00, -198657.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(105, 13, 8, 2, 8, 'Amor Matías Pintor Huguet', 122794.00, 122794.00, 0.00, 0.00, 49524.00, 73270.00, 0, 1, 0, 5, 12, 11020.00, 43020.00, 30250.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(106, 13, 8, 2, 8, 'Jesús Monreal-Osuna', 54421.00, 54421.00, 0.00, 0.00, 9631.00, 44790.00, 1, 3, 3, 9, 14, 16255.00, 113255.00, -68465.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(107, 13, 8, 2, 8, 'Casandra Cecilia Estevez Pou', 186192.00, 186192.00, 0.00, 0.00, 123318.00, 62874.00, 3, 1, 5, 8, 10, 7745.00, 128745.00, -65871.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(108, 13, 6, 2, 6, 'Leoncio Huguet Grau', 95683.00, 95683.00, 0.00, 0.00, 21055.00, 74628.00, 5, 4, 8, 7, 6, 13253.00, 213253.00, -138625.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(109, 13, 6, 2, 6, 'Carmela Baquero Castellanos', 146152.00, 146152.00, 0.00, 0.00, 72398.00, 73754.00, 2, 8, 7, 1, 11, 2831.00, 170831.00, -97077.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(110, 13, 8, 2, 8, 'Adoración Díaz-Briones', 168795.00, 168795.00, 0.00, 0.00, 5199.00, 163596.00, 2, 7, 9, 6, 6, 8152.00, 181152.00, -17556.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(111, 13, 9, 2, 9, 'Silvestre Saturnino Escribano Galindo', 32370.00, 32370.00, 0.00, 0.00, 2053.00, 30317.00, 1, 6, 7, 4, 13, 5717.00, 141717.00, -111400.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(112, 13, 8, 2, 8, 'Francisco Jose Fernández', 94360.00, 94360.00, 0.00, 0.00, 47125.00, 47235.00, 1, 10, 6, 4, 14, 16880.00, 188880.00, -141645.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:03'),
(113, 14, 19, 4, 19, 'Jimena Manrique Cortina', 11077.00, 11077.00, 0.00, 0.00, 7176.00, 3901.00, 0, 5, 6, 2, 16, 917.00, 100917.00, -97016.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:03'),
(114, 14, 20, 4, 20, 'Lucía Olivé Burgos', 144112.00, 144112.00, 0.00, 0.00, 108228.00, 35884.00, 4, 2, 6, 9, 9, 5620.00, 162620.00, -126736.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:03'),
(115, 14, 17, 4, 17, 'Azahar Saavedra Tirado', 174158.00, 174158.00, 0.00, 0.00, 7361.00, 166797.00, 0, 0, 1, 1, 7, 4846.00, 18846.00, 147951.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:03'),
(116, 14, 17, 4, 17, 'Haroldo del Bermudez', 57714.00, 57714.00, 0.00, 0.00, 23011.00, 34703.00, 5, 1, 4, 5, 15, 2007.00, 157007.00, -122304.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(117, 14, 17, 4, 17, 'Nidia Seguí Carretero', 33189.00, 33189.00, 0.00, 0.00, 21767.00, 11422.00, 1, 3, 7, 2, 14, 18572.00, 121572.00, -110150.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(118, 14, 18, 4, 18, 'Amador Pallarès', 94185.00, 94185.00, 0.00, 0.00, 62273.00, 31912.00, 5, 4, 8, 5, 7, 19765.00, 216765.00, -184853.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(119, 14, 20, 4, 20, 'Ismael Robles Salgado', 54686.00, 54686.00, 0.00, 0.00, 52739.00, 1947.00, 4, 6, 5, 3, 5, 4573.00, 180573.00, -178626.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(120, 15, 32, 7, 32, 'Cosme Busquets Figueroa', 22981.00, 22981.00, 0.00, 0.00, 12824.00, 10157.00, 1, 0, 4, 4, 3, 6277.00, 57277.00, -47120.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(121, 15, 33, 7, 33, 'Nydia Iborra Goñi', 107302.00, 107302.00, 0.00, 0.00, 74951.00, 32351.00, 3, 4, 3, 2, 19, 19482.00, 157482.00, -125131.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(122, 15, 34, 7, 34, 'Jenaro Manzanares Tapia', 150944.00, 150944.00, 0.00, 0.00, 93234.00, 57710.00, 5, 3, 8, 1, 8, 19804.00, 199804.00, -142094.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(123, 15, 31, 7, 31, 'Mario del Bonilla', 197018.00, 197018.00, 0.00, 0.00, 8078.00, 188940.00, 3, 7, 10, 9, 15, 9463.00, 222463.00, -33523.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(124, 15, 32, 7, 32, 'Encarnacion Mariscal Oller', 124628.00, 124628.00, 0.00, 0.00, 94822.00, 29806.00, 4, 7, 2, 9, 8, 6814.00, 192814.00, -163008.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(125, 15, 34, 7, 34, 'Isaac Vendrell Franch', 189239.00, 189239.00, 0.00, 0.00, 116420.00, 72819.00, 5, 1, 0, 10, 13, 16149.00, 159149.00, -86330.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(126, 15, 32, 7, 32, 'Aroa Cobos Berenguer', 187170.00, 187170.00, 0.00, 0.00, 58247.00, 128923.00, 3, 0, 7, 8, 12, 5058.00, 128058.00, 865.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(127, 15, 31, 7, 31, 'Ignacia Santamaría Bastida', 59827.00, 59827.00, 0.00, 0.00, 26441.00, 33386.00, 5, 6, 8, 2, 8, 4319.00, 216319.00, -182933.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(128, 15, 32, 7, 32, 'Alex Guijarro Canales', 119010.00, 119010.00, 0.00, 0.00, 34008.00, 85002.00, 2, 4, 6, 9, 18, 1890.00, 147890.00, -62888.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(129, 15, 32, 7, 32, 'Amílcar Arnau Flores', 60459.00, 60459.00, 0.00, 0.00, 40113.00, 20346.00, 0, 5, 7, 1, 16, 19248.00, 122248.00, -101902.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(130, 15, 34, 7, 34, 'Evelia Tejero-Madrid', 73802.00, 73802.00, 0.00, 0.00, 26993.00, 46809.00, 4, 10, 4, 0, 9, 13711.00, 222711.00, -175902.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(131, 15, 34, 7, 34, 'Feliciano Celso Blanch Pineda', 75520.00, 75520.00, 0.00, 0.00, 69854.00, 5666.00, 1, 0, 4, 3, 4, 11101.00, 61101.00, -55435.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(132, 15, 32, 7, 32, 'Ariadna del Boix', 132237.00, 132237.00, 0.00, 0.00, 49180.00, 83057.00, 5, 3, 8, 1, 4, 12777.00, 188777.00, -105720.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(133, 15, 31, 7, 31, 'Espiridión Cesar Mateu Avilés', 187380.00, 187380.00, 0.00, 0.00, 73110.00, 114270.00, 5, 5, 1, 7, 3, 10464.00, 182464.00, -68194.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(134, 15, 31, 7, 31, 'Jovita Sarita Carnero Pujol', 188358.00, 188358.00, 0.00, 0.00, 57906.00, 130452.00, 0, 3, 3, 0, 11, 13423.00, 69423.00, 61029.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(135, 16, 22, 5, 22, 'Juan Luis Llorens-Ferrer', 135211.00, 135211.00, 0.00, 0.00, 128025.00, 7186.00, 2, 2, 4, 7, 1, 9469.00, 104469.00, -97283.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(136, 16, 21, 5, 21, 'Cándida Bernad Tenorio', 40854.00, 40854.00, 0.00, 0.00, 37833.00, 3021.00, 0, 8, 8, 6, 16, 19598.00, 167598.00, -164577.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(137, 16, 24, 5, 24, 'Inocencio Sandoval Bellido', 86112.00, 86112.00, 0.00, 0.00, 25539.00, 60573.00, 4, 10, 0, 10, 7, 12148.00, 219148.00, -158575.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(138, 16, 23, 5, 23, 'Jenny Escalona Domingo', 35240.00, 35240.00, 0.00, 0.00, 23729.00, 11511.00, 0, 7, 3, 9, 10, 11381.00, 124381.00, -112870.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(139, 16, 23, 5, 23, 'Luís Catalán Moliner', 23344.00, 23344.00, 0.00, 0.00, 6354.00, 16990.00, 1, 0, 7, 1, 17, 6309.00, 80309.00, -63319.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(140, 16, 24, 5, 24, 'Adriana Marquez Marti', 104158.00, 104158.00, 0.00, 0.00, 49443.00, 54715.00, 1, 1, 9, 8, 4, 17988.00, 112988.00, -58273.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(141, 17, 6, 2, 6, 'Selena Coll Sales', 143737.00, 143737.00, 0.00, 0.00, 40253.00, 103484.00, 1, 8, 7, 7, 17, 9861.00, 175861.00, -72377.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(142, 17, 10, 2, 10, 'Matías Baeza Garmendia', 134074.00, 134074.00, 0.00, 0.00, 76764.00, 57310.00, 2, 9, 3, 7, 4, 7238.00, 170238.00, -112928.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(143, 17, 7, 2, 7, 'Noemí Portillo Ariño', 56655.00, 56655.00, 0.00, 0.00, 12607.00, 44048.00, 3, 5, 2, 6, 0, 13791.00, 145791.00, -101743.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(144, 17, 8, 2, 8, 'Rosario de Ropero', 196231.00, 196231.00, 0.00, 0.00, 165531.00, 30700.00, 0, 5, 5, 1, 1, 119.00, 78119.00, -47419.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(145, 17, 6, 2, 6, 'Emilio Pulido', 132893.00, 132893.00, 0.00, 0.00, 120021.00, 12872.00, 5, 7, 9, 1, 12, 14475.00, 243475.00, -230603.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(146, 18, 21, 5, 21, 'Angelita Segura Carreño', 131338.00, 131338.00, 0.00, 0.00, 105710.00, 25628.00, 3, 3, 8, 1, 20, 7577.00, 159577.00, -133949.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(147, 18, 24, 5, 24, 'Rolando Cortés Sanjuan', 118580.00, 118580.00, 0.00, 0.00, 111296.00, 7284.00, 2, 0, 6, 3, 3, 15231.00, 94231.00, -86947.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(148, 18, 21, 5, 21, 'Natividad Zamora Zurita', 120795.00, 120795.00, 0.00, 0.00, 90265.00, 30530.00, 4, 1, 9, 6, 13, 3192.00, 163192.00, -132662.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(149, 18, 21, 5, 21, 'Amalia de Domínguez', 54452.00, 54452.00, 0.00, 0.00, 19792.00, 34660.00, 3, 0, 0, 6, 14, 10744.00, 96744.00, -62084.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(150, 18, 24, 5, 24, 'María Lupe Carrión Nicolau', 172958.00, 172958.00, 0.00, 0.00, 163717.00, 9241.00, 1, 0, 8, 1, 4, 13329.00, 79329.00, -70088.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(151, 18, 22, 5, 22, 'Noelia Casal Burgos', 100025.00, 100025.00, 0.00, 0.00, 4980.00, 95045.00, 1, 5, 5, 5, 19, 16206.00, 140206.00, -45161.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(152, 18, 22, 5, 22, 'Isaías Guadalupe Carro Herrera', 147824.00, 147824.00, 0.00, 0.00, 32283.00, 115541.00, 4, 8, 1, 10, 13, 19790.00, 217790.00, -102249.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(153, 18, 21, 5, 21, 'Benigno Nogués', 194085.00, 194085.00, 0.00, 0.00, 75478.00, 118607.00, 3, 1, 9, 6, 8, 14319.00, 149319.00, -30712.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(154, 18, 23, 5, 23, 'Amelia Sierra Bastida', 178852.00, 178852.00, 0.00, 0.00, 4132.00, 174720.00, 0, 8, 8, 2, 18, 15749.00, 157749.00, 16971.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(155, 18, 23, 5, 23, 'Salvador Santamaría', 122301.00, 122301.00, 0.00, 0.00, 16245.00, 106056.00, 0, 8, 5, 7, 3, 11155.00, 133155.00, -27099.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(156, 18, 22, 5, 22, 'Wálter de Pineda', 93416.00, 93416.00, 0.00, 0.00, 32878.00, 60538.00, 4, 8, 10, 10, 18, 710.00, 248710.00, -188172.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(157, 18, 22, 5, 22, 'Marcelo Eutropio Arnau Coll', 21121.00, 21121.00, 0.00, 0.00, 5501.00, 15620.00, 3, 5, 5, 0, 3, 3173.00, 141173.00, -125553.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(158, 18, 23, 5, 23, 'Julio César Espada Palacio', 12760.00, 12760.00, 0.00, 0.00, 8802.00, 3958.00, 1, 8, 10, 9, 6, 15799.00, 189799.00, -185841.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(159, 18, 25, 5, 25, 'Onofre Murillo Saldaña', 6680.00, 6680.00, 0.00, 0.00, 6439.00, 241.00, 4, 8, 0, 8, 14, 8146.00, 198146.00, -197905.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(160, 19, 29, 6, 29, 'Florina Iniesta Quintanilla', 75985.00, 75985.00, 0.00, 0.00, 48849.00, 27136.00, 4, 6, 4, 8, 9, 3097.00, 188097.00, -160961.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(161, 19, 28, 6, 28, 'Mireia Diana Hoz Segarra', 181915.00, 181915.00, 0.00, 0.00, 83358.00, 98557.00, 5, 3, 9, 3, 16, 5117.00, 202117.00, -103560.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(162, 19, 28, 6, 28, 'Jose Manuel Querol Salom', 46669.00, 46669.00, 0.00, 0.00, 27983.00, 18686.00, 2, 10, 3, 7, 10, 6643.00, 185643.00, -166957.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(163, 19, 28, 6, 28, 'Patricia Blanch Barba', 147870.00, 147870.00, 0.00, 0.00, 140769.00, 7101.00, 2, 10, 9, 4, 19, 4368.00, 216368.00, -209267.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(164, 19, 29, 6, 29, 'Adolfo Esteban Agustín', 177497.00, 177497.00, 0.00, 0.00, 123678.00, 53819.00, 5, 5, 1, 0, 4, 17171.00, 176171.00, -122352.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(165, 20, 41, 9, 41, 'Víctor Saez Aznar', 144346.00, 144346.00, 0.00, 0.00, 13753.00, 130593.00, 1, 1, 7, 6, 15, 5007.00, 97007.00, 33586.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(166, 20, 43, 9, 43, 'Ale Lucena Morera', 110854.00, 110854.00, 0.00, 0.00, 70316.00, 40538.00, 3, 3, 3, 6, 18, 9440.00, 144440.00, -103902.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(167, 20, 44, 9, 44, 'Clarisa Garriga Oller', 175179.00, 175179.00, 0.00, 0.00, 127309.00, 47870.00, 5, 2, 2, 10, 13, 11693.00, 174693.00, -126823.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(168, 20, 45, 9, 45, 'Chus Valdés Alcalá', 14611.00, 14611.00, 0.00, 0.00, 6492.00, 8119.00, 1, 0, 4, 6, 5, 5915.00, 62915.00, -54796.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(169, 20, 42, 9, 42, 'Cristian del Vilanova', 21560.00, 21560.00, 0.00, 0.00, 20824.00, 736.00, 5, 2, 1, 2, 5, 14371.00, 148371.00, -147635.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(170, 20, 43, 9, 43, 'Xiomara Bueno Espada', 113123.00, 113123.00, 0.00, 0.00, 13349.00, 99774.00, 3, 4, 4, 7, 16, 13829.00, 163829.00, -64055.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(171, 20, 41, 9, 41, 'Haydée Seco Gárate', 26552.00, 26552.00, 0.00, 0.00, 1512.00, 25040.00, 1, 0, 4, 7, 1, 9661.00, 64661.00, -39621.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(172, 20, 41, 9, 41, 'Paulino Núñez Medina', 197188.00, 197188.00, 0.00, 0.00, 118973.00, 78215.00, 4, 2, 3, 10, 16, 12582.00, 163582.00, -85367.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(173, 20, 41, 9, 41, 'Borja Cristóbal Ramos Salgado', 193374.00, 193374.00, 0.00, 0.00, 45475.00, 147899.00, 2, 4, 7, 4, 14, 18487.00, 155487.00, -7588.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(174, 20, 42, 9, 42, 'Urbano Daniel Nieto Alcalá', 79661.00, 79661.00, 0.00, 0.00, 42132.00, 37529.00, 0, 2, 1, 1, 5, 18356.00, 50356.00, -12827.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(175, 20, 41, 9, 41, 'Rufina Fernandez Ledesma', 73101.00, 73101.00, 0.00, 0.00, 27739.00, 45362.00, 1, 10, 7, 0, 20, 10496.00, 185496.00, -140134.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(176, 20, 42, 9, 42, 'Edu de Tello', 176673.00, 176673.00, 0.00, 0.00, 70645.00, 106028.00, 0, 4, 2, 0, 0, 7863.00, 57863.00, 48165.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(177, 20, 44, 9, 44, 'Conrado Perea Rivas', 194398.00, 194398.00, 0.00, 0.00, 27195.00, 167203.00, 1, 0, 6, 8, 9, 178.00, 75178.00, 92025.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(178, 20, 44, 9, 44, 'Marina Ramirez Fuente', 31734.00, 31734.00, 0.00, 0.00, 13994.00, 17740.00, 3, 8, 8, 5, 2, 18389.00, 210389.00, -192649.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(179, 20, 44, 9, 44, 'Belén Maza-Jordán', 165190.00, 165190.00, 0.00, 0.00, 70978.00, 94212.00, 5, 8, 10, 7, 3, 16515.00, 263515.00, -169303.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:04'),
(180, 21, 31, 7, 31, 'Asunción Vaquero-García', 6396.00, 6396.00, 0.00, 0.00, 4658.00, 1738.00, 4, 0, 5, 8, 13, 9651.00, 143651.00, -141913.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(181, 21, 35, 7, 35, 'Santos Capdevila Llano', 99330.00, 99330.00, 0.00, 0.00, 69175.00, 30155.00, 2, 10, 8, 4, 13, 3620.00, 204620.00, -174465.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(182, 21, 31, 7, 31, 'Eugenia Lerma Asensio', 189251.00, 189251.00, 0.00, 0.00, 156054.00, 33197.00, 2, 4, 6, 6, 8, 15022.00, 145022.00, -111825.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(183, 21, 31, 7, 31, 'Teresita Guitart Quesada', 182925.00, 182925.00, 0.00, 0.00, 62147.00, 120778.00, 1, 1, 6, 7, 2, 12787.00, 88787.00, 31991.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(184, 21, 33, 7, 33, 'Silvia Casado Viana', 49085.00, 49085.00, 0.00, 0.00, 43821.00, 5264.00, 2, 5, 1, 1, 1, 7715.00, 105715.00, -100451.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(185, 21, 32, 7, 32, 'Evita Sevilla', 87183.00, 87183.00, 0.00, 0.00, 11963.00, 75220.00, 3, 6, 4, 2, 16, 7882.00, 167882.00, -92662.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(186, 21, 31, 7, 31, 'Leocadia Anita Montero Rincón', 171110.00, 171110.00, 0.00, 0.00, 158761.00, 12349.00, 5, 0, 7, 7, 7, 5189.00, 161189.00, -148840.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(187, 21, 34, 7, 34, 'Nayara Rosales Palau', 173894.00, 173894.00, 0.00, 0.00, 62875.00, 111019.00, 1, 3, 5, 5, 2, 18146.00, 105146.00, 5873.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(188, 21, 32, 7, 32, 'Juan Luis Chacón Armas', 7337.00, 7337.00, 0.00, 0.00, 4355.00, 2982.00, 5, 3, 2, 2, 18, 505.00, 162505.00, -159523.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(189, 21, 35, 7, 35, 'David Carro', 147557.00, 147557.00, 0.00, 0.00, 6090.00, 141467.00, 4, 1, 3, 10, 19, 17204.00, 161204.00, -19737.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(190, 21, 33, 7, 33, 'Valentín Aristides Ponce Roca', 192910.00, 192910.00, 0.00, 0.00, 59824.00, 133086.00, 3, 2, 9, 3, 6, 1796.00, 138796.00, -5710.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(191, 21, 34, 7, 34, 'Chus Palomino Lara', 55598.00, 55598.00, 0.00, 0.00, 19312.00, 36286.00, 0, 6, 7, 3, 5, 15006.00, 121006.00, -84720.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(192, 21, 31, 7, 31, 'Nadia Zamora Palomares', 101508.00, 101508.00, 0.00, 0.00, 35369.00, 66139.00, 1, 0, 3, 6, 5, 9382.00, 61382.00, 4757.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(193, 22, 36, 8, 36, 'Gisela de Coca', 131607.00, 131607.00, 0.00, 0.00, 61590.00, 70017.00, 5, 10, 10, 8, 15, 18381.00, 299381.00, -229364.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(194, 22, 37, 8, 37, 'Jordán Ordóñez Doménech', 193569.00, 193569.00, 0.00, 0.00, 94933.00, 98636.00, 0, 8, 3, 1, 12, 3565.00, 112565.00, -13929.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(195, 22, 39, 8, 39, 'Camila Calderón Arranz', 95642.00, 95642.00, 0.00, 0.00, 38294.00, 57348.00, 2, 9, 5, 10, 1, 14848.00, 190848.00, -133500.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(196, 22, 36, 8, 36, 'Florencia Jordán-Rosell', 9237.00, 9237.00, 0.00, 0.00, 5279.00, 3958.00, 2, 9, 7, 8, 13, 591.00, 194591.00, -190633.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(197, 22, 36, 8, 36, 'Belen Parejo-Pozuelo', 94443.00, 94443.00, 0.00, 0.00, 72300.00, 22143.00, 0, 3, 9, 6, 7, 8125.00, 102125.00, -79982.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(198, 22, 39, 8, 39, 'Ema Gabaldón Oller', 181511.00, 181511.00, 0.00, 0.00, 173156.00, 8355.00, 4, 3, 0, 3, 2, 9926.00, 127926.00, -119571.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(199, 22, 38, 8, 38, 'Pepito Leonardo Saavedra Villegas', 16961.00, 16961.00, 0.00, 0.00, 35.00, 16926.00, 5, 7, 5, 10, 20, 5582.00, 240582.00, -223656.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(200, 22, 37, 8, 37, 'Zacarías Fernández Manuel', 132193.00, 132193.00, 0.00, 0.00, 95104.00, 37089.00, 4, 7, 8, 5, 7, 19042.00, 226042.00, -188953.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(201, 22, 38, 8, 38, 'Sandalio Cabrero', 106428.00, 106428.00, 0.00, 0.00, 64770.00, 41658.00, 4, 4, 9, 2, 16, 2294.00, 187294.00, -145636.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(202, 23, 17, 4, 17, 'Ainoa Barba Fuente', 157381.00, 157381.00, 0.00, 0.00, 49143.00, 108238.00, 5, 2, 2, 10, 15, 11763.00, 176763.00, -68525.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(203, 23, 19, 4, 19, 'Dani Carreras', 20302.00, 20302.00, 0.00, 0.00, 10551.00, 9751.00, 1, 8, 1, 0, 2, 3391.00, 110391.00, -100640.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(204, 23, 16, 4, 16, 'Pascuala Máxima Julián Olivares', 138077.00, 138077.00, 0.00, 0.00, 39557.00, 98520.00, 2, 3, 0, 0, 16, 8954.00, 94954.00, 3566.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(205, 23, 19, 4, 19, 'Gerónimo Madrigal Diaz', 106690.00, 106690.00, 0.00, 0.00, 12953.00, 93737.00, 2, 2, 7, 7, 17, 13416.00, 139416.00, -45679.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(206, 23, 17, 4, 17, 'Yago Mármol', 74940.00, 74940.00, 0.00, 0.00, 27937.00, 47003.00, 3, 8, 5, 1, 0, 2852.00, 169852.00, -122849.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(207, 23, 18, 4, 18, 'Inés Malo Barrena', 108509.00, 108509.00, 0.00, 0.00, 21991.00, 86518.00, 2, 6, 6, 9, 7, 17521.00, 172521.00, -86003.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(208, 23, 20, 4, 20, 'Alba Custodia Ricart Vega', 185200.00, 185200.00, 0.00, 0.00, 107078.00, 78122.00, 2, 3, 6, 8, 0, 345.00, 116345.00, -38223.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(209, 23, 17, 4, 17, 'Cristian Lobo Rocamora', 131556.00, 131556.00, 0.00, 0.00, 101687.00, 29869.00, 1, 2, 5, 4, 18, 19533.00, 110533.00, -80664.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(210, 23, 18, 4, 18, 'Marcela María Jesús Haro Crespi', 71413.00, 71413.00, 0.00, 0.00, 10872.00, 60541.00, 3, 5, 5, 4, 14, 744.00, 157744.00, -97203.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(211, 23, 19, 4, 19, 'Guiomar del Llanos', 91019.00, 91019.00, 0.00, 0.00, 11245.00, 79774.00, 2, 9, 4, 2, 16, 7174.00, 177174.00, -97400.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(212, 24, 30, 6, 30, 'Aurelio Sacristán Sanchez', 121013.00, 121013.00, 0.00, 0.00, 16984.00, 104029.00, 0, 6, 2, 6, 7, 2808.00, 91808.00, 12221.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(213, 24, 29, 6, 29, 'Juan Carlos Lillo Paredes', 74704.00, 74704.00, 0.00, 0.00, 45206.00, 29498.00, 0, 0, 6, 5, 1, 8896.00, 49896.00, -20398.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(214, 24, 26, 6, 26, 'Ovidio Patiño Manzano', 49275.00, 49275.00, 0.00, 0.00, 42883.00, 6392.00, 1, 4, 8, 0, 3, 6348.00, 109348.00, -102956.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(215, 24, 28, 6, 28, 'Flavio Díez Martin', 135892.00, 135892.00, 0.00, 0.00, 107368.00, 28524.00, 3, 0, 9, 9, 14, 1893.00, 138893.00, -110369.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(216, 24, 28, 6, 28, 'Lope Fernández Rodríguez', 118499.00, 118499.00, 0.00, 0.00, 106689.00, 11810.00, 0, 7, 5, 6, 7, 14220.00, 128220.00, -116410.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(217, 24, 26, 6, 26, 'Blanca Sanchez', 117374.00, 117374.00, 0.00, 0.00, 115987.00, 1387.00, 5, 10, 0, 9, 11, 13405.00, 242405.00, -241018.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(218, 24, 29, 6, 29, 'Rico Tovar Montero', 120071.00, 120071.00, 0.00, 0.00, 7613.00, 112458.00, 1, 0, 4, 6, 13, 10979.00, 75979.00, 36479.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(219, 24, 26, 6, 26, 'Jose Miguel Crespi Aranda', 149718.00, 149718.00, 0.00, 0.00, 1920.00, 147798.00, 1, 7, 9, 8, 4, 19901.00, 174901.00, -27103.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(220, 24, 27, 6, 27, 'Victoriano Rincón Mayol', 92940.00, 92940.00, 0.00, 0.00, 77949.00, 14991.00, 3, 2, 2, 3, 12, 12762.00, 120762.00, -105771.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(221, 25, 27, 6, 27, 'Victorino Agustín Novoa', 173582.00, 173582.00, 0.00, 0.00, 59452.00, 114130.00, 0, 0, 9, 5, 19, 15121.00, 89121.00, 25009.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(222, 25, 30, 6, 30, 'Rosalía Miguel-Guijarro', 150599.00, 150599.00, 0.00, 0.00, 78652.00, 71947.00, 4, 0, 6, 8, 15, 18633.00, 159633.00, -87686.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(223, 25, 28, 6, 28, 'Carmela Gual Robles', 48166.00, 48166.00, 0.00, 0.00, 37403.00, 10763.00, 2, 1, 5, 10, 0, 2863.00, 97863.00, -87100.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(224, 25, 26, 6, 26, 'Esteban Baena Guijarro', 51311.00, 51311.00, 0.00, 0.00, 34957.00, 16354.00, 3, 10, 2, 9, 10, 10213.00, 208213.00, -191859.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(225, 25, 28, 6, 28, 'Juan Pablo Dávila Suárez', 17862.00, 17862.00, 0.00, 0.00, 7781.00, 10081.00, 1, 10, 5, 6, 14, 4756.00, 175756.00, -165675.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(226, 25, 28, 6, 28, 'Dora Rocha Alberdi', 59462.00, 59462.00, 0.00, 0.00, 25901.00, 33561.00, 5, 3, 7, 10, 15, 5275.00, 205275.00, -171714.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(227, 25, 28, 6, 28, 'Cornelio Cerdá', 138555.00, 138555.00, 0.00, 0.00, 36864.00, 101691.00, 3, 9, 7, 10, 20, 3839.00, 228839.00, -127148.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04');
INSERT INTO `lectura_maquina` (`id_lectura`, `id_cierre`, `id_maquina`, `id_zona`, `numero_maquina`, `nombre_persona`, `caja`, `numeral`, `prestamos`, `redbank`, `retiros`, `total_caja`, `billete_20000`, `billete_10000`, `billete_5000`, `billete_2000`, `billete_1000`, `monedas_total`, `total_entregado`, `descuadre`, `nota`, `created_by`, `created_at`) VALUES
(228, 25, 29, 6, 29, 'Venceslás Calderón Llano', 181311.00, 181311.00, 0.00, 0.00, 29763.00, 151548.00, 0, 8, 1, 10, 20, 17651.00, 142651.00, 8897.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(229, 25, 26, 6, 26, 'Flavio Polo Miralles', 171485.00, 171485.00, 0.00, 0.00, 140929.00, 30556.00, 0, 6, 2, 3, 20, 777.00, 96777.00, -66221.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(230, 25, 30, 6, 30, 'Amor Arenas-Garcés', 113814.00, 113814.00, 0.00, 0.00, 93983.00, 19831.00, 4, 4, 9, 7, 16, 7900.00, 202900.00, -183069.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(231, 25, 30, 6, 30, 'Dora Valderrama Salamanca', 82699.00, 82699.00, 0.00, 0.00, 22004.00, 60695.00, 5, 2, 3, 9, 11, 8292.00, 172292.00, -111597.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(232, 26, 1, 1, 1, 'Máximo Carlito Almagro Naranjo', 95448.00, 95448.00, 0.00, 0.00, 30097.00, 65351.00, 0, 1, 10, 5, 0, 6445.00, 76445.00, -11094.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(233, 26, 2, 1, 2, 'Porfirio Augusto Ribas Feijoo', 148378.00, 148378.00, 0.00, 0.00, 50238.00, 98140.00, 3, 2, 0, 3, 1, 8399.00, 95399.00, 2741.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(234, 26, 5, 1, 5, 'Lina Parra Pedrosa', 121866.00, 121866.00, 0.00, 0.00, 79676.00, 42190.00, 0, 5, 1, 1, 2, 12924.00, 71924.00, -29734.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(235, 26, 2, 1, 2, 'Cayetana Chaves-Martín', 48921.00, 48921.00, 0.00, 0.00, 36260.00, 12661.00, 5, 1, 7, 1, 16, 8092.00, 171092.00, -158431.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(236, 26, 4, 1, 4, 'Feliciano Suárez-Botella', 197871.00, 197871.00, 0.00, 0.00, 67757.00, 130114.00, 1, 2, 9, 7, 12, 2812.00, 113812.00, 16302.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(237, 26, 4, 1, 4, 'Manu Olmo Suárez', 111439.00, 111439.00, 0.00, 0.00, 3078.00, 108361.00, 3, 2, 0, 7, 15, 19846.00, 128846.00, -20485.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(238, 26, 1, 1, 1, 'Ricarda Puig-Cid', 109513.00, 109513.00, 0.00, 0.00, 90188.00, 19325.00, 2, 7, 10, 0, 5, 18037.00, 183037.00, -163712.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(239, 26, 3, 1, 3, 'Ámbar Ugarte Perales', 16733.00, 16733.00, 0.00, 0.00, 6614.00, 10119.00, 5, 3, 2, 9, 1, 427.00, 159427.00, -149308.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(240, 26, 2, 1, 2, 'Dorotea Seguí Marti', 102163.00, 102163.00, 0.00, 0.00, 83974.00, 18189.00, 4, 8, 2, 8, 3, 16289.00, 205289.00, -187100.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(241, 26, 5, 1, 5, 'Lupe Zaragoza-Peñalver', 100874.00, 100874.00, 0.00, 0.00, 28375.00, 72499.00, 3, 7, 9, 2, 6, 11893.00, 196893.00, -124394.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:04'),
(242, 27, 19, 4, 19, 'Claudio Pinedo', 177461.00, 177461.00, 0.00, 0.00, 94022.00, 83439.00, 1, 0, 7, 6, 0, 970.00, 67970.00, 15469.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(243, 27, 18, 4, 18, 'Eloísa Araujo Tejero', 142482.00, 142482.00, 0.00, 0.00, 77404.00, 65078.00, 3, 2, 7, 9, 14, 11060.00, 158060.00, -92982.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(244, 27, 16, 4, 16, 'Tamara Diez Barrera', 80780.00, 80780.00, 0.00, 0.00, 36723.00, 44057.00, 1, 2, 0, 10, 16, 9749.00, 85749.00, -41692.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(245, 27, 17, 4, 17, 'Aurelia Planas Merino', 156531.00, 156531.00, 0.00, 0.00, 22448.00, 134083.00, 4, 1, 1, 6, 12, 6490.00, 125490.00, 8593.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(246, 27, 17, 4, 17, 'Lisandro Saldaña Manrique', 89056.00, 89056.00, 0.00, 0.00, 47642.00, 41414.00, 2, 6, 0, 3, 4, 9070.00, 119070.00, -77656.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(247, 27, 17, 4, 17, 'Santos Menendez', 98004.00, 98004.00, 0.00, 0.00, 26343.00, 71661.00, 3, 6, 0, 3, 6, 5698.00, 137698.00, -66037.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(248, 27, 20, 4, 20, 'Cristina Figuerola Baeza', 160767.00, 160767.00, 0.00, 0.00, 97780.00, 62987.00, 5, 2, 5, 6, 2, 9106.00, 168106.00, -105119.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(249, 27, 20, 4, 20, 'Cebrián Murcia', 5014.00, 5014.00, 0.00, 0.00, 2427.00, 2587.00, 0, 5, 6, 9, 10, 6848.00, 114848.00, -112261.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(250, 27, 19, 4, 19, 'Clarisa del Fajardo', 126460.00, 126460.00, 0.00, 0.00, 27621.00, 98839.00, 4, 3, 4, 1, 12, 4306.00, 148306.00, -49467.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(251, 27, 17, 4, 17, 'Marciano Hierro Uría', 127351.00, 127351.00, 0.00, 0.00, 95145.00, 32206.00, 1, 8, 5, 9, 6, 10438.00, 159438.00, -127232.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(252, 27, 18, 4, 18, 'Octavio Santiago Anglada', 40711.00, 40711.00, 0.00, 0.00, 38408.00, 2303.00, 5, 2, 4, 0, 6, 4021.00, 150021.00, -147718.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(253, 27, 19, 4, 19, 'Claudia del Llamas', 76697.00, 76697.00, 0.00, 0.00, 18052.00, 58645.00, 5, 3, 2, 0, 10, 13572.00, 163572.00, -104927.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:04'),
(254, 28, 22, 5, 22, 'Cornelio Carbonell', 8117.00, 8117.00, 0.00, 0.00, 7913.00, 204.00, 2, 8, 4, 9, 19, 18035.00, 195035.00, -194831.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(255, 28, 21, 5, 21, 'Hernán Castillo', 28451.00, 28451.00, 0.00, 0.00, 3886.00, 24565.00, 4, 2, 2, 6, 0, 13113.00, 135113.00, -110548.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(256, 28, 21, 5, 21, 'Melchor Batalla Vila', 78890.00, 78890.00, 0.00, 0.00, 25360.00, 53530.00, 2, 4, 4, 1, 15, 13247.00, 130247.00, -76717.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(257, 28, 25, 5, 25, 'Débora Páez Mate', 48584.00, 48584.00, 0.00, 0.00, 2129.00, 46455.00, 3, 1, 6, 6, 7, 8487.00, 127487.00, -81032.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(258, 28, 21, 5, 21, 'Soraya Rebeca Cuéllar Ferrando', 80648.00, 80648.00, 0.00, 0.00, 56294.00, 24354.00, 3, 2, 0, 2, 5, 1288.00, 90288.00, -65934.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:04'),
(259, 29, 9, 2, 9, 'Lola Clarisa Torres Blazquez', 39114.00, 39114.00, 0.00, 0.00, 36624.00, 2490.00, 3, 4, 10, 4, 7, 16893.00, 181893.00, -179403.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:05'),
(260, 29, 6, 2, 6, 'Lope Antúnez Peláez', 72633.00, 72633.00, 0.00, 0.00, 44812.00, 27821.00, 3, 3, 0, 0, 3, 5648.00, 98648.00, -70827.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:05'),
(261, 29, 7, 2, 7, 'Hugo Ropero', 97586.00, 97586.00, 0.00, 0.00, 45111.00, 52475.00, 0, 3, 6, 7, 17, 9596.00, 100596.00, -48121.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:05'),
(262, 29, 9, 2, 9, 'José Juanito Marí Alsina', 53485.00, 53485.00, 0.00, 0.00, 24164.00, 29321.00, 0, 4, 5, 0, 6, 8130.00, 79130.00, -49809.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:05'),
(263, 29, 8, 2, 8, 'Roberto del Boada', 5625.00, 5625.00, 0.00, 0.00, 727.00, 4898.00, 5, 1, 6, 2, 8, 13585.00, 165585.00, -160687.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:05'),
(264, 29, 6, 2, 6, 'Germán Palma-Sánchez', 140053.00, 140053.00, 0.00, 0.00, 85254.00, 54799.00, 5, 2, 6, 4, 15, 18006.00, 191006.00, -136207.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:05'),
(265, 29, 6, 2, 6, 'Águeda Alfaro Sobrino', 174908.00, 174908.00, 0.00, 0.00, 55371.00, 119537.00, 5, 2, 8, 3, 12, 18666.00, 196666.00, -77129.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:05'),
(266, 30, 19, 4, 19, 'Eufemia Marqués Ribera', 68068.00, 68068.00, 0.00, 0.00, 34871.00, 33197.00, 5, 10, 0, 1, 15, 11267.00, 228267.00, -195070.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:05'),
(267, 30, 19, 4, 19, 'Ariadna Alejandra Ramírez Fabra', 165246.00, 165246.00, 0.00, 0.00, 142769.00, 22477.00, 0, 0, 5, 5, 10, 12487.00, 57487.00, -35010.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:05'),
(268, 30, 17, 4, 17, 'Carolina Márquez', 72037.00, 72037.00, 0.00, 0.00, 947.00, 71090.00, 0, 7, 10, 3, 15, 5047.00, 146047.00, -74957.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:05'),
(269, 30, 19, 4, 19, 'Josefa de Zamora', 146699.00, 146699.00, 0.00, 0.00, 40628.00, 106071.00, 0, 9, 6, 1, 18, 2452.00, 142452.00, -36381.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:05'),
(270, 30, 17, 4, 17, 'Candelas Salazar-Guerra', 46355.00, 46355.00, 0.00, 0.00, 6420.00, 39935.00, 5, 6, 10, 9, 0, 475.00, 228475.00, -188540.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:05'),
(271, 30, 20, 4, 20, 'Jordán Cuesta Carmona', 114421.00, 114421.00, 0.00, 0.00, 95102.00, 19319.00, 4, 3, 5, 10, 17, 14525.00, 186525.00, -167206.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:05'),
(272, 30, 19, 4, 19, 'Alonso Palomares Rueda', 135482.00, 135482.00, 0.00, 0.00, 76845.00, 58637.00, 0, 1, 4, 4, 14, 5316.00, 57316.00, 1321.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:05'),
(273, 31, 30, 6, 30, 'Bárbara del Alba', 40239.00, 40239.00, 0.00, 0.00, 26367.00, 13872.00, 2, 10, 8, 2, 4, 14976.00, 202976.00, -189104.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(274, 31, 26, 6, 26, 'Rosalva Martin Real', 32007.00, 32007.00, 0.00, 0.00, 1009.00, 30998.00, 3, 10, 8, 10, 17, 7937.00, 244937.00, -213939.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(275, 31, 29, 6, 29, 'Desiderio de Arco', 198284.00, 198284.00, 0.00, 0.00, 144529.00, 53755.00, 4, 5, 10, 4, 2, 4612.00, 194612.00, -140857.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(276, 31, 30, 6, 30, 'Lucía Perea Abril', 109413.00, 109413.00, 0.00, 0.00, 68719.00, 40694.00, 4, 8, 9, 6, 12, 5571.00, 234571.00, -193877.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(277, 31, 26, 6, 26, 'Heriberto Barranco', 185561.00, 185561.00, 0.00, 0.00, 136080.00, 49481.00, 0, 1, 3, 2, 9, 15522.00, 53522.00, -4041.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(278, 31, 30, 6, 30, 'Georgina Salom Pellicer', 119569.00, 119569.00, 0.00, 0.00, 118013.00, 1556.00, 4, 6, 1, 1, 16, 3212.00, 166212.00, -164656.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(279, 31, 29, 6, 29, 'Gisela Caparrós Sarabia', 195111.00, 195111.00, 0.00, 0.00, 77149.00, 117962.00, 4, 5, 4, 3, 20, 5404.00, 181404.00, -63442.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(280, 31, 28, 6, 28, 'Flavio Clemente-Armas', 128872.00, 128872.00, 0.00, 0.00, 81792.00, 47080.00, 2, 9, 5, 0, 12, 2643.00, 169643.00, -122563.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(281, 31, 27, 6, 27, 'Carlito Villalba Falcón', 166979.00, 166979.00, 0.00, 0.00, 159961.00, 7018.00, 0, 0, 6, 8, 3, 10941.00, 59941.00, -52923.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(282, 31, 27, 6, 27, 'María Teresa Palomares Zabala', 52983.00, 52983.00, 0.00, 0.00, 46051.00, 6932.00, 5, 1, 6, 1, 12, 875.00, 154875.00, -147943.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(283, 31, 29, 6, 29, 'Aitana Plana Conde', 35212.00, 35212.00, 0.00, 0.00, 13037.00, 22175.00, 3, 1, 7, 8, 10, 9986.00, 140986.00, -118811.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(284, 31, 28, 6, 28, 'Baltasar de Rosado', 180537.00, 180537.00, 0.00, 0.00, 167933.00, 12604.00, 2, 10, 8, 9, 20, 3209.00, 221209.00, -208605.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(285, 31, 27, 6, 27, 'Duilio Castells Huertas', 14795.00, 14795.00, 0.00, 0.00, 774.00, 14021.00, 4, 10, 4, 2, 2, 10532.00, 216532.00, -202511.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(286, 32, 41, 9, 41, 'Nidia Guillen Pastor', 192583.00, 192583.00, 0.00, 0.00, 111784.00, 80799.00, 5, 2, 5, 1, 2, 5606.00, 154606.00, -73807.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(287, 32, 45, 9, 45, 'Clarisa Mendez Granados', 111968.00, 111968.00, 0.00, 0.00, 3637.00, 108331.00, 5, 5, 2, 1, 12, 796.00, 174796.00, -66465.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(288, 32, 42, 9, 42, 'Gonzalo del Aguilera', 123933.00, 123933.00, 0.00, 0.00, 52778.00, 71155.00, 5, 4, 8, 0, 6, 6080.00, 192080.00, -120925.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(289, 32, 43, 9, 43, 'Domingo Atienza-Valverde', 116730.00, 116730.00, 0.00, 0.00, 76862.00, 39868.00, 0, 4, 9, 8, 17, 8762.00, 126762.00, -86894.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(290, 32, 45, 9, 45, 'Marcelino Jódar Lastra', 93582.00, 93582.00, 0.00, 0.00, 31267.00, 62315.00, 1, 4, 4, 2, 5, 8498.00, 97498.00, -35183.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(291, 32, 41, 9, 41, 'Francisco Javier Carbonell', 166559.00, 166559.00, 0.00, 0.00, 80234.00, 86325.00, 3, 7, 4, 4, 20, 10193.00, 188193.00, -101868.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(292, 32, 43, 9, 43, 'Feliciano de Benavides', 169177.00, 169177.00, 0.00, 0.00, 69020.00, 100157.00, 4, 3, 10, 3, 19, 226.00, 185226.00, -85069.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(293, 32, 44, 9, 44, 'Hipólito Amat Pino', 171831.00, 171831.00, 0.00, 0.00, 149173.00, 22658.00, 3, 5, 3, 8, 10, 1955.00, 152955.00, -130297.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(294, 32, 44, 9, 44, 'Fernanda Sureda Lorenzo', 153549.00, 153549.00, 0.00, 0.00, 118305.00, 35244.00, 0, 8, 6, 8, 16, 18421.00, 160421.00, -125177.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(295, 33, 6, 2, 6, 'Amaya Pavón Serna', 196784.00, 196784.00, 0.00, 0.00, 42252.00, 154532.00, 0, 10, 3, 1, 4, 2667.00, 123667.00, 30865.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:05'),
(296, 33, 6, 2, 6, 'Fausto Sancho', 46426.00, 46426.00, 0.00, 0.00, 15257.00, 31169.00, 5, 7, 0, 0, 13, 15732.00, 198732.00, -167563.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:05'),
(297, 33, 10, 2, 10, 'Heriberto Alberola', 112110.00, 112110.00, 0.00, 0.00, 101723.00, 10387.00, 4, 5, 0, 4, 9, 8028.00, 155028.00, -144641.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:05'),
(298, 33, 8, 2, 8, 'Donato Villa Ledesma', 55946.00, 55946.00, 0.00, 0.00, 18738.00, 37208.00, 2, 6, 3, 6, 16, 13808.00, 156808.00, -119600.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:05'),
(299, 33, 10, 2, 10, 'Valentín de Benet', 87059.00, 87059.00, 0.00, 0.00, 54883.00, 32176.00, 4, 1, 7, 9, 3, 12322.00, 158322.00, -126146.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:05'),
(300, 33, 6, 2, 6, 'Amelia Hernández Angulo', 126972.00, 126972.00, 0.00, 0.00, 97038.00, 29934.00, 0, 0, 1, 3, 6, 8004.00, 25004.00, 4930.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:05'),
(301, 33, 7, 2, 7, 'Alma Borrás', 131240.00, 131240.00, 0.00, 0.00, 86062.00, 45178.00, 2, 3, 1, 6, 11, 11973.00, 109973.00, -64795.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:05'),
(302, 33, 8, 2, 8, 'Zoraida Belén Bonet Donaire', 77098.00, 77098.00, 0.00, 0.00, 37329.00, 39769.00, 5, 4, 5, 9, 9, 18345.00, 210345.00, -170576.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:05'),
(303, 33, 10, 2, 10, 'Javi Pons-Garcia', 14699.00, 14699.00, 0.00, 0.00, 3872.00, 10827.00, 1, 1, 1, 1, 12, 9116.00, 58116.00, -47289.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:05'),
(304, 34, 2, 1, 2, 'Dominga Suarez Lumbreras', 171225.00, 171225.00, 0.00, 0.00, 124332.00, 46893.00, 0, 0, 7, 2, 3, 5278.00, 47278.00, -385.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(305, 34, 1, 1, 1, 'Lisandro Nogués Huguet', 33033.00, 33033.00, 0.00, 0.00, 28836.00, 4197.00, 2, 2, 3, 9, 17, 3294.00, 113294.00, -109097.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(306, 34, 2, 1, 2, 'Teodoro Jove-Olmedo', 185208.00, 185208.00, 0.00, 0.00, 130181.00, 55027.00, 2, 4, 6, 10, 8, 14423.00, 152423.00, -97396.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(307, 34, 4, 1, 4, 'Amado Trujillo-Aranda', 180439.00, 180439.00, 0.00, 0.00, 152490.00, 27949.00, 3, 3, 1, 8, 17, 8908.00, 136908.00, -108959.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(308, 34, 2, 1, 2, 'Berta de Luján', 190251.00, 190251.00, 0.00, 0.00, 167997.00, 22254.00, 3, 7, 2, 3, 2, 12166.00, 160166.00, -137912.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(309, 34, 5, 1, 5, 'Victoriano Porras-Antúnez', 186099.00, 186099.00, 0.00, 0.00, 56133.00, 129966.00, 5, 10, 2, 10, 1, 16659.00, 247659.00, -117693.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(310, 34, 5, 1, 5, 'Palmira Palacio Díez', 6286.00, 6286.00, 0.00, 0.00, 3935.00, 2351.00, 3, 0, 0, 2, 6, 18848.00, 88848.00, -86497.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(311, 34, 4, 1, 4, 'Aureliano Alcaraz Vallejo', 121515.00, 121515.00, 0.00, 0.00, 99119.00, 22396.00, 4, 1, 4, 1, 2, 8280.00, 122280.00, -99884.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(312, 34, 4, 1, 4, 'Bienvenida Vázquez Carranza', 147195.00, 147195.00, 0.00, 0.00, 24734.00, 122461.00, 4, 2, 10, 2, 1, 6057.00, 161057.00, -38596.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(313, 34, 4, 1, 4, 'Elvira Montalbán Mendizábal', 52035.00, 52035.00, 0.00, 0.00, 13198.00, 38837.00, 2, 5, 0, 1, 10, 19114.00, 121114.00, -82277.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(314, 34, 4, 1, 4, 'Carla Benavente Amo', 196964.00, 196964.00, 0.00, 0.00, 21743.00, 175221.00, 3, 6, 2, 10, 16, 17635.00, 183635.00, -8414.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(315, 34, 5, 1, 5, 'María Jesús Tomás Morata', 154338.00, 154338.00, 0.00, 0.00, 36545.00, 117793.00, 4, 5, 6, 4, 15, 15530.00, 198530.00, -80737.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(316, 34, 4, 1, 4, 'Ismael Almansa Lobato', 76327.00, 76327.00, 0.00, 0.00, 16116.00, 60211.00, 4, 4, 2, 7, 17, 18527.00, 179527.00, -119316.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(317, 35, 23, 5, 23, 'Saturnina Izaguirre Iglesias', 49094.00, 49094.00, 0.00, 0.00, 2202.00, 46892.00, 4, 4, 6, 7, 6, 5059.00, 175059.00, -128167.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(318, 35, 21, 5, 21, 'Ale Becerra Briones', 58020.00, 58020.00, 0.00, 0.00, 17529.00, 40491.00, 3, 10, 3, 9, 8, 12205.00, 213205.00, -172714.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(319, 35, 25, 5, 25, 'Luis Ángel de Exposito', 184690.00, 184690.00, 0.00, 0.00, 146844.00, 37846.00, 2, 1, 2, 4, 13, 18584.00, 99584.00, -61738.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(320, 35, 22, 5, 22, 'Piedad Pinedo Arteaga', 136701.00, 136701.00, 0.00, 0.00, 19723.00, 116978.00, 2, 0, 10, 7, 17, 5192.00, 126192.00, -9214.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(321, 35, 21, 5, 21, 'Isa Julián Ródenas', 87785.00, 87785.00, 0.00, 0.00, 78629.00, 9156.00, 4, 3, 0, 10, 1, 16854.00, 147854.00, -138698.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(322, 36, 35, 7, 35, 'Baudelio Mariscal', 176116.00, 176116.00, 0.00, 0.00, 102008.00, 74108.00, 2, 10, 3, 4, 4, 10537.00, 177537.00, -103429.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(323, 36, 32, 7, 32, 'Dora de Pedrosa', 10437.00, 10437.00, 0.00, 0.00, 3847.00, 6590.00, 0, 7, 0, 9, 3, 13295.00, 104295.00, -97705.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(324, 36, 34, 7, 34, 'Anita Ricart Tur', 108507.00, 108507.00, 0.00, 0.00, 84463.00, 24044.00, 1, 9, 0, 5, 18, 19242.00, 157242.00, -133198.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(325, 36, 32, 7, 32, 'Guiomar Meléndez Escolano', 113316.00, 113316.00, 0.00, 0.00, 107023.00, 6293.00, 5, 6, 3, 1, 15, 11626.00, 203626.00, -197333.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(326, 36, 32, 7, 32, 'Constanza de Boada', 50827.00, 50827.00, 0.00, 0.00, 46797.00, 4030.00, 4, 5, 0, 8, 1, 8336.00, 155336.00, -151306.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(327, 36, 34, 7, 34, 'Joaquín Tiburcio Baquero Estevez', 60729.00, 60729.00, 0.00, 0.00, 54643.00, 6086.00, 3, 1, 3, 9, 4, 18709.00, 125709.00, -119623.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(328, 36, 32, 7, 32, 'Faustino de Fuentes', 11326.00, 11326.00, 0.00, 0.00, 1920.00, 9406.00, 3, 0, 1, 10, 11, 9727.00, 105727.00, -96321.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(329, 36, 34, 7, 34, 'Leire Esteban Olmo', 81326.00, 81326.00, 0.00, 0.00, 5202.00, 76124.00, 2, 7, 2, 7, 1, 13739.00, 148739.00, -72615.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(330, 36, 34, 7, 34, 'Santos Emilio Rebollo Soto', 75789.00, 75789.00, 0.00, 0.00, 1873.00, 73916.00, 1, 6, 0, 3, 14, 5143.00, 105143.00, -31227.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(331, 37, 2, 1, 2, 'Jose Miguel Aguilar', 157236.00, 157236.00, 0.00, 0.00, 121262.00, 35974.00, 4, 6, 2, 7, 4, 1714.00, 169714.00, -133740.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(332, 37, 2, 1, 2, 'Noemí Maldonado Barbero', 24662.00, 24662.00, 0.00, 0.00, 22658.00, 2004.00, 4, 1, 2, 2, 13, 1800.00, 118800.00, -116796.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(333, 37, 4, 1, 4, 'Salomé Coca-Solana', 61085.00, 61085.00, 0.00, 0.00, 52391.00, 8694.00, 4, 4, 10, 6, 13, 7481.00, 202481.00, -193787.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(334, 37, 3, 1, 3, 'Zaida Mateo-Cerro', 165892.00, 165892.00, 0.00, 0.00, 47553.00, 118339.00, 2, 2, 1, 6, 8, 6271.00, 91271.00, 27068.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(335, 37, 2, 1, 2, 'Eufemia Campoy Huerta', 168476.00, 168476.00, 0.00, 0.00, 38644.00, 129832.00, 0, 2, 7, 10, 7, 1134.00, 83134.00, 46698.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(336, 37, 4, 1, 4, 'Goyo Jose Miguel Frutos Angulo', 56679.00, 56679.00, 0.00, 0.00, 51688.00, 4991.00, 4, 5, 10, 8, 7, 15733.00, 218733.00, -213742.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(337, 37, 2, 1, 2, 'Curro Mancebo Bustos', 5689.00, 5689.00, 0.00, 0.00, 3975.00, 1714.00, 1, 9, 9, 1, 8, 11526.00, 176526.00, -174812.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(338, 38, 11, 3, 11, 'Rosalía Falcó Millán', 126804.00, 126804.00, 0.00, 0.00, 50290.00, 76514.00, 4, 0, 6, 5, 12, 6859.00, 138859.00, -62345.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:05'),
(339, 38, 11, 3, 11, 'Pepito Ramón Estévez Quirós', 134810.00, 134810.00, 0.00, 0.00, 500.00, 134310.00, 0, 4, 10, 10, 15, 11633.00, 136633.00, -2323.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:05'),
(340, 38, 14, 3, 14, 'Yésica Andrés Oliver', 54877.00, 54877.00, 0.00, 0.00, 43814.00, 11063.00, 4, 1, 1, 4, 18, 8783.00, 129783.00, -118720.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:05'),
(341, 38, 15, 3, 15, 'Francisco Jose Francisco Sanjuan Crespo', 31307.00, 31307.00, 0.00, 0.00, 10635.00, 20672.00, 4, 2, 9, 7, 9, 18349.00, 186349.00, -165677.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:05'),
(342, 38, 13, 3, 13, 'Danilo Gárate-Bernad', 168359.00, 168359.00, 0.00, 0.00, 95242.00, 73117.00, 2, 5, 8, 7, 1, 19632.00, 164632.00, -91515.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:05'),
(343, 39, 35, 7, 35, 'Manola Vergara', 76700.00, 76700.00, 0.00, 0.00, 21228.00, 55472.00, 2, 4, 9, 8, 7, 7493.00, 155493.00, -100021.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(344, 39, 34, 7, 34, 'Fátima María Teresa Castillo Carbajo', 100149.00, 100149.00, 0.00, 0.00, 70612.00, 29537.00, 2, 5, 0, 1, 1, 11011.00, 104011.00, -74474.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(345, 39, 31, 7, 31, 'Florentino Macias', 123333.00, 123333.00, 0.00, 0.00, 45726.00, 77607.00, 4, 3, 8, 7, 18, 19340.00, 201340.00, -123733.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(346, 39, 33, 7, 33, 'Ángel del Rivera', 195660.00, 195660.00, 0.00, 0.00, 54847.00, 140813.00, 5, 7, 9, 6, 16, 16595.00, 259595.00, -118782.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(347, 39, 32, 7, 32, 'Evaristo Arnau Esparza', 127073.00, 127073.00, 0.00, 0.00, 123855.00, 3218.00, 0, 9, 4, 10, 5, 1282.00, 136282.00, -133064.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(348, 39, 35, 7, 35, 'Amado Cantón', 69948.00, 69948.00, 0.00, 0.00, 22891.00, 47057.00, 4, 5, 6, 4, 17, 4499.00, 189499.00, -142442.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(349, 39, 32, 7, 32, 'Hernán Laguna Campoy', 65373.00, 65373.00, 0.00, 0.00, 64682.00, 691.00, 0, 0, 8, 8, 10, 8728.00, 74728.00, -74037.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(350, 39, 31, 7, 31, 'Isabel Guillén Sales', 133649.00, 133649.00, 0.00, 0.00, 77428.00, 56221.00, 4, 2, 3, 0, 4, 6428.00, 125428.00, -69207.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(351, 39, 35, 7, 35, 'Primitivo Alegria Guzman', 156773.00, 156773.00, 0.00, 0.00, 86716.00, 70057.00, 3, 6, 10, 2, 1, 6233.00, 181233.00, -111176.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(352, 39, 31, 7, 31, 'Candela de Andrés', 165673.00, 165673.00, 0.00, 0.00, 106349.00, 59324.00, 1, 4, 0, 9, 7, 8933.00, 93933.00, -34609.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(353, 39, 31, 7, 31, 'Lilia Loida Cifuentes Borrell', 116789.00, 116789.00, 0.00, 0.00, 5161.00, 111628.00, 0, 10, 3, 0, 19, 13443.00, 147443.00, -35815.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(354, 39, 35, 7, 35, 'Andrea Marco Nevado', 182015.00, 182015.00, 0.00, 0.00, 139412.00, 42603.00, 3, 6, 10, 5, 10, 9881.00, 199881.00, -157278.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(355, 39, 34, 7, 34, 'Óscar de Morillo', 26967.00, 26967.00, 0.00, 0.00, 21513.00, 5454.00, 2, 2, 3, 1, 5, 2086.00, 84086.00, -78632.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(356, 39, 34, 7, 34, 'Judith Ojeda', 175117.00, 175117.00, 0.00, 0.00, 43517.00, 131600.00, 0, 2, 0, 1, 17, 7192.00, 46192.00, 85408.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(357, 39, 35, 7, 35, 'Adriana Jordán Puig', 133965.00, 133965.00, 0.00, 0.00, 117287.00, 16678.00, 3, 0, 7, 1, 14, 541.00, 111541.00, -94863.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(358, 40, 11, 3, 11, 'Georgina Iriarte Zabala', 49916.00, 49916.00, 0.00, 0.00, 25034.00, 24882.00, 5, 5, 6, 0, 1, 15966.00, 196966.00, -172084.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(359, 40, 12, 3, 12, 'Fátima Claudia Zurita Gisbert', 121862.00, 121862.00, 0.00, 0.00, 96887.00, 24975.00, 0, 4, 8, 10, 1, 14540.00, 115540.00, -90565.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(360, 40, 11, 3, 11, 'Plácido Cifuentes', 128769.00, 128769.00, 0.00, 0.00, 56021.00, 72748.00, 3, 2, 9, 0, 3, 12970.00, 140970.00, -68222.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(361, 40, 11, 3, 11, 'Isa Almazán Villalobos', 103264.00, 103264.00, 0.00, 0.00, 7862.00, 95402.00, 2, 3, 8, 3, 19, 15000.00, 150000.00, -54598.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(362, 40, 12, 3, 12, 'Obdulia Agustín Juan', 197513.00, 197513.00, 0.00, 0.00, 181315.00, 16198.00, 2, 8, 0, 3, 1, 14589.00, 141589.00, -125391.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(363, 40, 11, 3, 11, 'Lucho Antúnez Folch', 191011.00, 191011.00, 0.00, 0.00, 64570.00, 126441.00, 3, 6, 7, 0, 20, 16216.00, 191216.00, -64775.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(364, 40, 13, 3, 13, 'Gervasio Izaguirre Segovia', 188377.00, 188377.00, 0.00, 0.00, 2421.00, 185956.00, 1, 8, 6, 3, 4, 3287.00, 143287.00, 42669.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(365, 40, 13, 3, 13, 'Anita Celestina Palomino Barroso', 152911.00, 152911.00, 0.00, 0.00, 95005.00, 57906.00, 3, 3, 0, 5, 4, 3785.00, 107785.00, -49879.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(366, 40, 14, 3, 14, 'Nazaret Iglesia Sosa', 134066.00, 134066.00, 0.00, 0.00, 22881.00, 111185.00, 5, 5, 8, 6, 17, 12074.00, 231074.00, -119889.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(367, 40, 15, 3, 15, 'Silvia Bibiana Baeza Taboada', 73644.00, 73644.00, 0.00, 0.00, 3064.00, 70580.00, 5, 9, 6, 1, 6, 1676.00, 229676.00, -159096.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(368, 40, 13, 3, 13, 'Carlito Elorza Losada', 127737.00, 127737.00, 0.00, 0.00, 122121.00, 5616.00, 2, 3, 2, 7, 11, 3180.00, 108180.00, -102564.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(369, 41, 34, 7, 34, 'Nazaret de Torrent', 90835.00, 90835.00, 0.00, 0.00, 65473.00, 25362.00, 5, 5, 6, 7, 3, 18992.00, 215992.00, -190630.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(370, 41, 35, 7, 35, 'Marisela Neira Lorenzo', 141289.00, 141289.00, 0.00, 0.00, 7524.00, 133765.00, 4, 2, 2, 9, 10, 18848.00, 156848.00, -23083.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(371, 41, 34, 7, 34, 'Paola Galván-Córdoba', 171738.00, 171738.00, 0.00, 0.00, 106784.00, 64954.00, 0, 2, 3, 4, 7, 13799.00, 63799.00, 1155.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(372, 41, 32, 7, 32, 'Maribel Vidal Llanos', 26043.00, 26043.00, 0.00, 0.00, 2587.00, 23456.00, 2, 4, 2, 1, 9, 4044.00, 105044.00, -81588.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(373, 41, 31, 7, 31, 'Paz de Mateos', 196439.00, 196439.00, 0.00, 0.00, 155167.00, 41272.00, 5, 9, 9, 5, 1, 12525.00, 258525.00, -217253.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(374, 41, 32, 7, 32, 'Chucho Ramírez Ángel', 197974.00, 197974.00, 0.00, 0.00, 2919.00, 195055.00, 3, 9, 0, 6, 10, 11304.00, 183304.00, 11751.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(375, 41, 33, 7, 33, 'Prudencia Asenjo Leal', 123259.00, 123259.00, 0.00, 0.00, 85406.00, 37853.00, 3, 7, 10, 9, 3, 4532.00, 205532.00, -167679.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(376, 41, 33, 7, 33, 'Fito Donaire Feijoo', 60089.00, 60089.00, 0.00, 0.00, 9757.00, 50332.00, 5, 10, 6, 1, 14, 14133.00, 260133.00, -209801.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(377, 41, 34, 7, 34, 'Mónica Gracia Ariño', 109675.00, 109675.00, 0.00, 0.00, 100987.00, 8688.00, 5, 4, 0, 1, 20, 12283.00, 174283.00, -165595.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(378, 41, 32, 7, 32, 'Calixta Bosch Sancho', 144490.00, 144490.00, 0.00, 0.00, 141783.00, 2707.00, 0, 4, 10, 3, 15, 15300.00, 126300.00, -123593.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(379, 41, 31, 7, 31, 'Araceli de Navarro', 113824.00, 113824.00, 0.00, 0.00, 843.00, 112981.00, 3, 3, 8, 1, 10, 11890.00, 153890.00, -40909.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(380, 41, 34, 7, 34, 'Matilde Pulido Ribas', 99221.00, 99221.00, 0.00, 0.00, 2373.00, 96848.00, 0, 4, 7, 5, 1, 16497.00, 102497.00, -5649.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(381, 42, 17, 4, 17, 'Azahara Flores Cordero', 17617.00, 17617.00, 0.00, 0.00, 16067.00, 1550.00, 5, 9, 3, 5, 15, 8852.00, 238852.00, -237302.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(382, 42, 16, 4, 16, 'Miguel Villalobos Peralta', 49820.00, 49820.00, 0.00, 0.00, 41499.00, 8321.00, 2, 9, 3, 5, 6, 14792.00, 175792.00, -167471.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(383, 42, 19, 4, 19, 'Florencia Pineda Antúnez', 15846.00, 15846.00, 0.00, 0.00, 14167.00, 1679.00, 2, 9, 7, 9, 2, 13089.00, 198089.00, -196410.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(384, 42, 20, 4, 20, 'Pastora Quiroga', 66539.00, 66539.00, 0.00, 0.00, 6062.00, 60477.00, 4, 9, 6, 1, 20, 2842.00, 224842.00, -164365.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(385, 42, 20, 4, 20, 'Darío Cortes Pou', 18626.00, 18626.00, 0.00, 0.00, 7330.00, 11296.00, 0, 2, 5, 6, 2, 12953.00, 71953.00, -60657.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(386, 42, 19, 4, 19, 'Brígida Cabrera', 76438.00, 76438.00, 0.00, 0.00, 6318.00, 70120.00, 5, 5, 6, 9, 9, 15964.00, 222964.00, -152844.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(387, 42, 20, 4, 20, 'Kike Casas Carbajo', 188143.00, 188143.00, 0.00, 0.00, 14622.00, 173521.00, 3, 8, 4, 3, 12, 18192.00, 196192.00, -22671.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(388, 42, 17, 4, 17, 'Clara Fabregat Herrera', 33297.00, 33297.00, 0.00, 0.00, 26883.00, 6414.00, 3, 7, 6, 1, 17, 10883.00, 189883.00, -183469.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(389, 42, 16, 4, 16, 'Modesta Ramis Bejarano', 173358.00, 173358.00, 0.00, 0.00, 147083.00, 26275.00, 1, 1, 2, 5, 14, 8835.00, 72835.00, -46560.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(390, 42, 20, 4, 20, 'Jordana Alsina Bayón', 180269.00, 180269.00, 0.00, 0.00, 10744.00, 169525.00, 4, 5, 7, 5, 0, 17967.00, 192967.00, -23442.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(391, 42, 18, 4, 18, 'Marisol Borrego', 151630.00, 151630.00, 0.00, 0.00, 144322.00, 7308.00, 5, 3, 10, 6, 4, 11863.00, 207863.00, -200555.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(392, 42, 20, 4, 20, 'Bruno Oliver Espada', 138629.00, 138629.00, 0.00, 0.00, 63725.00, 74904.00, 0, 9, 10, 0, 9, 18770.00, 167770.00, -92866.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(393, 42, 20, 4, 20, 'Fabiana Millán', 116318.00, 116318.00, 0.00, 0.00, 72838.00, 43480.00, 3, 5, 9, 2, 18, 15398.00, 192398.00, -148918.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(394, 42, 20, 4, 20, 'Renato Blanes Angulo', 14950.00, 14950.00, 0.00, 0.00, 11822.00, 3128.00, 4, 0, 0, 0, 13, 12947.00, 105947.00, -102819.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(395, 42, 20, 4, 20, 'Gervasio Mariano Tejada Pastor', 82871.00, 82871.00, 0.00, 0.00, 43705.00, 39166.00, 3, 2, 2, 0, 5, 17607.00, 112607.00, -73441.00, 'Registro de prueba generado automáticamente.', 4, '2025-11-24 20:51:05'),
(396, 43, 22, 5, 22, 'Cruz de Barco', 116115.00, 116115.00, 0.00, 0.00, 36809.00, 79306.00, 2, 0, 4, 7, 1, 18021.00, 93021.00, -13715.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(397, 43, 22, 5, 22, 'Lupe Tovar Falcó', 5467.00, 5467.00, 0.00, 0.00, 2344.00, 3123.00, 3, 10, 8, 0, 12, 10354.00, 222354.00, -219231.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(398, 43, 25, 5, 25, 'Seve Gallo-Clemente', 57440.00, 57440.00, 0.00, 0.00, 32371.00, 25069.00, 4, 0, 6, 6, 2, 16370.00, 140370.00, -115301.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(399, 43, 25, 5, 25, 'Alma Verdejo Bayona', 133771.00, 133771.00, 0.00, 0.00, 71857.00, 61914.00, 1, 9, 2, 0, 6, 13911.00, 139911.00, -77997.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(400, 43, 24, 5, 24, 'Herberto Alfonso Saura', 124775.00, 124775.00, 0.00, 0.00, 110083.00, 14692.00, 1, 4, 1, 4, 4, 11613.00, 88613.00, -73921.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(401, 43, 24, 5, 24, 'Chus Alberola Rivera', 133443.00, 133443.00, 0.00, 0.00, 123908.00, 9535.00, 1, 9, 0, 1, 17, 16192.00, 145192.00, -135657.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(402, 43, 23, 5, 23, 'Sebastian Font Doménech', 181058.00, 181058.00, 0.00, 0.00, 96181.00, 84877.00, 1, 7, 6, 3, 14, 2736.00, 142736.00, -57859.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(403, 43, 22, 5, 22, 'Lilia Rocamora Perera', 189383.00, 189383.00, 0.00, 0.00, 169614.00, 19769.00, 2, 0, 10, 6, 6, 304.00, 108304.00, -88535.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(404, 43, 25, 5, 25, 'Anastasia Hernando Cifuentes', 71150.00, 71150.00, 0.00, 0.00, 27060.00, 44090.00, 3, 3, 8, 3, 13, 5811.00, 154811.00, -110721.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(405, 43, 21, 5, 21, 'Virginia del Vázquez', 123507.00, 123507.00, 0.00, 0.00, 9284.00, 114223.00, 2, 6, 6, 9, 9, 7438.00, 164438.00, -50215.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(406, 43, 23, 5, 23, 'Rita Palomares Becerra', 108491.00, 108491.00, 0.00, 0.00, 37740.00, 70751.00, 4, 10, 3, 7, 1, 5662.00, 215662.00, -144911.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(407, 43, 24, 5, 24, 'Sabas Fajardo Caro', 196942.00, 196942.00, 0.00, 0.00, 33068.00, 163874.00, 5, 2, 5, 3, 7, 18668.00, 176668.00, -12794.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(408, 43, 24, 5, 24, 'Cleto Adadia Perelló', 41656.00, 41656.00, 0.00, 0.00, 24792.00, 16864.00, 5, 4, 5, 6, 15, 15371.00, 207371.00, -190507.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(409, 43, 25, 5, 25, 'Perlita Herranz Tejada', 172518.00, 172518.00, 0.00, 0.00, 159195.00, 13323.00, 5, 9, 6, 1, 0, 15470.00, 237470.00, -224147.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(410, 43, 21, 5, 21, 'Herminio Rincón Rubio', 176625.00, 176625.00, 0.00, 0.00, 58033.00, 118592.00, 5, 8, 3, 4, 11, 8746.00, 222746.00, -104154.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(411, 44, 30, 6, 30, 'Abril Moya Velasco', 84880.00, 84880.00, 0.00, 0.00, 59853.00, 25027.00, 4, 6, 10, 10, 9, 11551.00, 230551.00, -205524.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(412, 44, 26, 6, 26, 'Mirta Riba Fernández', 189562.00, 189562.00, 0.00, 0.00, 20404.00, 169158.00, 3, 9, 6, 4, 7, 5746.00, 200746.00, -31588.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(413, 44, 26, 6, 26, 'Celestina Pol Palmer', 48326.00, 48326.00, 0.00, 0.00, 5110.00, 43216.00, 1, 1, 7, 4, 6, 8674.00, 87674.00, -44458.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(414, 44, 26, 6, 26, 'Paula Rivero Tomás', 186953.00, 186953.00, 0.00, 0.00, 81419.00, 105534.00, 1, 9, 2, 8, 13, 10553.00, 159553.00, -54019.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(415, 44, 29, 6, 29, 'Leonel Bernabé Dueñas Uribe', 47322.00, 47322.00, 0.00, 0.00, 828.00, 46494.00, 3, 2, 1, 9, 6, 13451.00, 122451.00, -75957.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(416, 44, 29, 6, 29, 'Ceferino Múgica-Serna', 43651.00, 43651.00, 0.00, 0.00, 12388.00, 31263.00, 1, 3, 5, 7, 4, 818.00, 93818.00, -62555.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(417, 44, 29, 6, 29, 'Azeneth Agustí Ferrán', 137199.00, 137199.00, 0.00, 0.00, 37658.00, 99541.00, 4, 6, 1, 5, 19, 2170.00, 176170.00, -76629.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(418, 44, 26, 6, 26, 'Edelmira Riquelme Montero', 66554.00, 66554.00, 0.00, 0.00, 42058.00, 24496.00, 4, 5, 8, 9, 8, 1034.00, 197034.00, -172538.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(419, 44, 26, 6, 26, 'Consuelo Pol Collado', 191525.00, 191525.00, 0.00, 0.00, 51305.00, 140220.00, 2, 8, 7, 5, 1, 9027.00, 175027.00, -34807.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(420, 44, 30, 6, 30, 'Joan Guillen', 180688.00, 180688.00, 0.00, 0.00, 163077.00, 17611.00, 2, 8, 9, 3, 5, 11746.00, 187746.00, -170135.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(421, 44, 30, 6, 30, 'Fabio Lucas López', 105921.00, 105921.00, 0.00, 0.00, 34536.00, 71385.00, 0, 5, 8, 10, 12, 3406.00, 125406.00, -54021.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(422, 44, 26, 6, 26, 'Pedro Ropero Iglesias', 177862.00, 177862.00, 0.00, 0.00, 52135.00, 125727.00, 0, 3, 1, 1, 6, 15626.00, 58626.00, 67101.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(423, 44, 30, 6, 30, 'Hugo Paniagua Blazquez', 86112.00, 86112.00, 0.00, 0.00, 64788.00, 21324.00, 4, 10, 2, 6, 18, 1195.00, 221195.00, -199871.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(424, 44, 30, 6, 30, 'Artemio Sevilla Escobar', 110115.00, 110115.00, 0.00, 0.00, 94981.00, 15134.00, 1, 5, 8, 1, 6, 7947.00, 125947.00, -110813.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(425, 44, 29, 6, 29, 'Joan Torrecilla Izquierdo', 67057.00, 67057.00, 0.00, 0.00, 41861.00, 25196.00, 2, 10, 2, 8, 6, 15918.00, 187918.00, -162722.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(426, 45, 25, 5, 25, 'Leyre Madrigal-Sabater', 118780.00, 118780.00, 0.00, 0.00, 42076.00, 76704.00, 4, 6, 4, 3, 9, 3593.00, 178593.00, -101889.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(427, 45, 23, 5, 23, 'Galo Pinilla Arnaiz', 64557.00, 64557.00, 0.00, 0.00, 22959.00, 41598.00, 2, 1, 1, 4, 20, 8242.00, 91242.00, -49644.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(428, 45, 23, 5, 23, 'Jose Ramón Gil Arco', 65052.00, 65052.00, 0.00, 0.00, 45702.00, 19350.00, 3, 7, 6, 7, 5, 9089.00, 188089.00, -168739.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(429, 45, 25, 5, 25, 'Odalys Terrón', 178175.00, 178175.00, 0.00, 0.00, 127315.00, 50860.00, 0, 10, 7, 5, 18, 9342.00, 172342.00, -121482.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(430, 45, 25, 5, 25, 'Lina de Ferrer', 113387.00, 113387.00, 0.00, 0.00, 61671.00, 51716.00, 1, 10, 0, 6, 13, 13895.00, 158895.00, -107179.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:05'),
(431, 45, 24, 5, 24, 'Felipe Tejada', 186436.00, 186436.00, 0.00, 0.00, 73358.00, 113078.00, 0, 2, 9, 6, 8, 18138.00, 103138.00, 9940.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:06'),
(432, 45, 25, 5, 25, 'Amada Méndez', 123905.00, 123905.00, 0.00, 0.00, 61772.00, 62133.00, 2, 9, 10, 3, 12, 16371.00, 214371.00, -152238.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:06'),
(433, 45, 22, 5, 22, 'Aura Silva Camacho', 164231.00, 164231.00, 0.00, 0.00, 78614.00, 85617.00, 5, 6, 8, 0, 10, 13270.00, 223270.00, -137653.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:06'),
(434, 45, 23, 5, 23, 'Florinda Diego Morell', 168652.00, 168652.00, 0.00, 0.00, 57139.00, 111513.00, 5, 3, 7, 4, 8, 3825.00, 184825.00, -73312.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:06'),
(435, 45, 22, 5, 22, 'René Estevez Segura', 157470.00, 157470.00, 0.00, 0.00, 21732.00, 135738.00, 3, 3, 7, 0, 6, 14345.00, 145345.00, -9607.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:06'),
(436, 45, 25, 5, 25, 'Adrián Pla Oliver', 193042.00, 193042.00, 0.00, 0.00, 124891.00, 68151.00, 5, 9, 6, 0, 15, 10014.00, 245014.00, -176863.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:06'),
(437, 45, 25, 5, 25, 'Julio César Requena Peñas', 179364.00, 179364.00, 0.00, 0.00, 81887.00, 97477.00, 0, 3, 0, 10, 8, 4356.00, 62356.00, 35121.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:06'),
(438, 45, 22, 5, 22, 'Fernando Andrés Blanes', 164415.00, 164415.00, 0.00, 0.00, 153058.00, 11357.00, 0, 1, 5, 9, 1, 3030.00, 57030.00, -45673.00, 'Registro de prueba generado automáticamente.', 2, '2025-11-24 20:51:06'),
(439, 46, 21, 5, 21, 'Marianela Aguirre Saez', 197620.00, 197620.00, 0.00, 0.00, 81014.00, 116606.00, 1, 8, 6, 10, 8, 8037.00, 166037.00, -49431.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(440, 46, 25, 5, 25, 'Jacobo Sanz Quiroga', 199190.00, 199190.00, 0.00, 0.00, 182200.00, 16990.00, 5, 0, 2, 7, 2, 17339.00, 143339.00, -126349.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(441, 46, 21, 5, 21, 'Dorotea Moles Pedro', 106387.00, 106387.00, 0.00, 0.00, 25879.00, 80508.00, 1, 6, 4, 9, 6, 4965.00, 128965.00, -48457.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(442, 46, 23, 5, 23, 'Tamara Reig-Bernat', 160668.00, 160668.00, 0.00, 0.00, 99215.00, 61453.00, 5, 5, 0, 2, 7, 4833.00, 165833.00, -104380.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(443, 46, 25, 5, 25, 'Quique Puente Almagro', 80932.00, 80932.00, 0.00, 0.00, 36943.00, 43989.00, 4, 10, 5, 3, 20, 14938.00, 245938.00, -201949.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(444, 46, 25, 5, 25, 'Eligia Elorza Suarez', 12844.00, 12844.00, 0.00, 0.00, 6693.00, 6151.00, 0, 7, 6, 10, 0, 11004.00, 131004.00, -124853.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(445, 46, 25, 5, 25, 'Modesto Vázquez Bertrán', 133325.00, 133325.00, 0.00, 0.00, 10673.00, 122652.00, 2, 1, 0, 10, 9, 12427.00, 91427.00, 31225.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(446, 47, 11, 3, 11, 'Íñigo de Santiago', 86096.00, 86096.00, 0.00, 0.00, 32464.00, 53632.00, 3, 4, 2, 3, 18, 2618.00, 136618.00, -82986.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(447, 47, 15, 3, 15, 'Lucía Rivero Gonzalez', 146862.00, 146862.00, 0.00, 0.00, 112369.00, 34493.00, 1, 9, 8, 0, 9, 18374.00, 177374.00, -142881.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(448, 47, 15, 3, 15, 'Amaro Barreda Bauzà', 64287.00, 64287.00, 0.00, 0.00, 20081.00, 44206.00, 2, 10, 9, 10, 13, 7511.00, 225511.00, -181305.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(449, 47, 12, 3, 12, 'Galo Galván Tejada', 36901.00, 36901.00, 0.00, 0.00, 33756.00, 3145.00, 3, 8, 1, 2, 20, 3335.00, 172335.00, -169190.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(450, 47, 13, 3, 13, 'Omar Benítez Ros', 101025.00, 101025.00, 0.00, 0.00, 43920.00, 57105.00, 1, 8, 4, 5, 14, 12008.00, 156008.00, -98903.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(451, 47, 11, 3, 11, 'Alejandra Ferrándiz Alvarado', 63952.00, 63952.00, 0.00, 0.00, 5423.00, 58529.00, 0, 1, 0, 9, 11, 15205.00, 54205.00, 4324.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(452, 47, 15, 3, 15, 'Narciso Sola Lumbreras', 108863.00, 108863.00, 0.00, 0.00, 41107.00, 67756.00, 4, 3, 1, 0, 19, 19141.00, 153141.00, -85385.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(453, 47, 14, 3, 14, 'Lope Galiano Esteve', 195155.00, 195155.00, 0.00, 0.00, 83865.00, 111290.00, 0, 7, 5, 6, 20, 17398.00, 144398.00, -33108.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(454, 47, 14, 3, 14, 'Gastón Miranda-Gallo', 50686.00, 50686.00, 0.00, 0.00, 9381.00, 41305.00, 0, 6, 8, 1, 3, 19887.00, 124887.00, -83582.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06');
INSERT INTO `lectura_maquina` (`id_lectura`, `id_cierre`, `id_maquina`, `id_zona`, `numero_maquina`, `nombre_persona`, `caja`, `numeral`, `prestamos`, `redbank`, `retiros`, `total_caja`, `billete_20000`, `billete_10000`, `billete_5000`, `billete_2000`, `billete_1000`, `monedas_total`, `total_entregado`, `descuadre`, `nota`, `created_by`, `created_at`) VALUES
(455, 47, 15, 3, 15, 'Rebeca Rivera Toledo', 7553.00, 7553.00, 0.00, 0.00, 4366.00, 3187.00, 3, 2, 5, 7, 16, 9866.00, 144866.00, -141679.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(456, 47, 15, 3, 15, 'Darío Torralba Lluch', 149638.00, 149638.00, 0.00, 0.00, 119132.00, 30506.00, 3, 10, 1, 8, 17, 3580.00, 201580.00, -171074.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(457, 48, 2, 1, 2, 'Martina Luís-Bravo', 5017.00, 5017.00, 0.00, 0.00, 1763.00, 3254.00, 0, 0, 2, 1, 8, 13182.00, 33182.00, -29928.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:06'),
(458, 48, 4, 1, 4, 'Marcial Sainz Hoyos', 153729.00, 153729.00, 0.00, 0.00, 63109.00, 90620.00, 4, 3, 7, 3, 15, 11458.00, 177458.00, -86838.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:06'),
(459, 48, 1, 1, 1, 'Eusebio Ariño Becerra', 87423.00, 87423.00, 0.00, 0.00, 78275.00, 9148.00, 1, 4, 3, 8, 9, 14560.00, 114560.00, -105412.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:06'),
(460, 48, 3, 1, 3, 'Mirta de España', 15634.00, 15634.00, 0.00, 0.00, 13655.00, 1979.00, 4, 1, 10, 5, 3, 12205.00, 165205.00, -163226.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:06'),
(461, 48, 5, 1, 5, 'Chus Crespo Arribas', 160504.00, 160504.00, 0.00, 0.00, 10383.00, 150121.00, 3, 7, 5, 9, 5, 5541.00, 183541.00, -33420.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:06'),
(462, 49, 33, 7, 33, 'Santos Calderón Garcés', 51310.00, 51310.00, 0.00, 0.00, 36232.00, 15078.00, 1, 2, 2, 2, 14, 3478.00, 71478.00, -56400.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(463, 49, 33, 7, 33, 'Guiomar Jordán Tirado', 45621.00, 45621.00, 0.00, 0.00, 34525.00, 11096.00, 4, 9, 4, 7, 0, 497.00, 204497.00, -193401.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(464, 49, 35, 7, 35, 'Elena Cantero Cases', 185596.00, 185596.00, 0.00, 0.00, 21016.00, 164580.00, 3, 9, 7, 3, 17, 7177.00, 215177.00, -50597.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(465, 49, 34, 7, 34, 'Lucho Llabrés-Vazquez', 76646.00, 76646.00, 0.00, 0.00, 55827.00, 20819.00, 0, 5, 3, 7, 6, 19177.00, 104177.00, -83358.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(466, 49, 35, 7, 35, 'Salvador Bueno Gómez', 126150.00, 126150.00, 0.00, 0.00, 101782.00, 24368.00, 3, 2, 3, 8, 4, 16968.00, 131968.00, -107600.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(467, 49, 32, 7, 32, 'Lourdes Benet Amat', 183675.00, 183675.00, 0.00, 0.00, 146238.00, 37437.00, 0, 2, 9, 2, 3, 15681.00, 87681.00, -50244.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(468, 49, 33, 7, 33, 'Curro Murillo', 110283.00, 110283.00, 0.00, 0.00, 73087.00, 37196.00, 0, 2, 10, 0, 9, 18788.00, 97788.00, -60592.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(469, 50, 4, 1, 4, 'Lucía Castro-Franco', 127506.00, 127506.00, 0.00, 0.00, 48987.00, 78519.00, 2, 4, 3, 0, 1, 5915.00, 101915.00, -23396.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(470, 50, 4, 1, 4, 'Loida Mateo Escudero', 51914.00, 51914.00, 0.00, 0.00, 50680.00, 1234.00, 2, 7, 2, 0, 14, 2451.00, 136451.00, -135217.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(471, 50, 3, 1, 3, 'Clarisa del Heras', 150733.00, 150733.00, 0.00, 0.00, 100652.00, 50081.00, 0, 7, 8, 6, 9, 9844.00, 140844.00, -90763.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(472, 50, 2, 1, 2, 'Vito Cirino Morán Llobet', 67687.00, 67687.00, 0.00, 0.00, 48227.00, 19460.00, 0, 0, 8, 2, 7, 6649.00, 57649.00, -38189.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(473, 50, 1, 1, 1, 'Tiburcio Álamo-Goicoechea', 75240.00, 75240.00, 0.00, 0.00, 53114.00, 22126.00, 3, 0, 6, 7, 20, 4190.00, 128190.00, -106064.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(474, 50, 1, 1, 1, 'Zacarías Mendizábal Huguet', 6523.00, 6523.00, 0.00, 0.00, 4836.00, 1687.00, 4, 4, 9, 1, 15, 17661.00, 199661.00, -197974.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(475, 51, 35, 7, 35, 'Elías Terrón Chaves', 27628.00, 27628.00, 0.00, 0.00, 25243.00, 2385.00, 1, 6, 1, 9, 4, 12934.00, 119934.00, -117549.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(476, 51, 33, 7, 33, 'Leire Graciela Valle Mulet', 70867.00, 70867.00, 0.00, 0.00, 64250.00, 6617.00, 5, 5, 10, 2, 6, 6587.00, 216587.00, -209970.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(477, 51, 34, 7, 34, 'Jessica Eli Bermejo Nicolás', 113909.00, 113909.00, 0.00, 0.00, 76807.00, 37102.00, 2, 6, 9, 2, 0, 19900.00, 168900.00, -131798.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(478, 51, 33, 7, 33, 'Claudia Ríos Fortuny', 126824.00, 126824.00, 0.00, 0.00, 124974.00, 1850.00, 1, 2, 4, 1, 10, 12749.00, 84749.00, -82899.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(479, 51, 31, 7, 31, 'Elisabet Castillo', 107126.00, 107126.00, 0.00, 0.00, 37339.00, 69787.00, 5, 5, 0, 9, 4, 16672.00, 188672.00, -118885.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(480, 51, 34, 7, 34, 'Ainoa Nebot Dueñas', 46911.00, 46911.00, 0.00, 0.00, 30130.00, 16781.00, 3, 9, 9, 2, 7, 18244.00, 224244.00, -207463.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(481, 51, 32, 7, 32, 'Arcelia Oliver-Aragón', 59351.00, 59351.00, 0.00, 0.00, 12786.00, 46565.00, 0, 3, 8, 6, 3, 5199.00, 90199.00, -43634.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(482, 51, 34, 7, 34, 'Roberta Peñas', 74754.00, 74754.00, 0.00, 0.00, 70740.00, 4014.00, 5, 10, 8, 1, 0, 8688.00, 250688.00, -246674.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(483, 51, 35, 7, 35, 'Ani Coronado Salvador', 79389.00, 79389.00, 0.00, 0.00, 64853.00, 14536.00, 4, 1, 8, 1, 2, 5373.00, 139373.00, -124837.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(484, 52, 5, 1, 5, 'Emma Gabaldón Sales', 86977.00, 86977.00, 0.00, 0.00, 9819.00, 77158.00, 1, 7, 3, 7, 11, 12940.00, 142940.00, -65782.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(485, 52, 1, 1, 1, 'Paula Botella Boix', 183264.00, 183264.00, 0.00, 0.00, 168632.00, 14632.00, 4, 0, 3, 3, 15, 11054.00, 127054.00, -112422.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(486, 52, 3, 1, 3, 'Vanesa del Almazán', 25532.00, 25532.00, 0.00, 0.00, 15870.00, 9662.00, 4, 0, 3, 1, 19, 11170.00, 127170.00, -117508.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(487, 52, 2, 1, 2, 'Ángela Falcón Hervás', 18051.00, 18051.00, 0.00, 0.00, 14106.00, 3945.00, 0, 7, 7, 8, 0, 6306.00, 127306.00, -123361.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(488, 52, 1, 1, 1, 'Armida Artigas Mendizábal', 136896.00, 136896.00, 0.00, 0.00, 52303.00, 84593.00, 4, 10, 5, 7, 9, 4961.00, 232961.00, -148368.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(489, 52, 1, 1, 1, 'Efraín Querol Botella', 154710.00, 154710.00, 0.00, 0.00, 79846.00, 74864.00, 2, 7, 6, 9, 1, 13238.00, 172238.00, -97374.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(490, 52, 5, 1, 5, 'Angelino Mateu', 138433.00, 138433.00, 0.00, 0.00, 77612.00, 60821.00, 0, 7, 10, 7, 15, 1550.00, 150550.00, -89729.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(491, 52, 3, 1, 3, 'Nélida Pombo Arranz', 132057.00, 132057.00, 0.00, 0.00, 69295.00, 62762.00, 1, 0, 2, 4, 16, 3864.00, 57864.00, 4898.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(492, 52, 1, 1, 1, 'Joaquina Cervera Correa', 42163.00, 42163.00, 0.00, 0.00, 18639.00, 23524.00, 1, 1, 0, 10, 10, 14229.00, 74229.00, -50705.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(493, 52, 1, 1, 1, 'Juan José Heras-Rodríguez', 61848.00, 61848.00, 0.00, 0.00, 38047.00, 23801.00, 3, 0, 2, 2, 17, 12923.00, 103923.00, -80122.00, 'Registro de prueba generado automáticamente.', 3, '2025-11-24 20:51:06'),
(494, 53, 41, 9, 41, 'Dan del Barbero', 38986.00, 38986.00, 0.00, 0.00, 11243.00, 27743.00, 0, 9, 6, 0, 17, 9212.00, 146212.00, -118469.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:06'),
(495, 53, 43, 9, 43, 'Palmira Gascón Ángel', 136368.00, 136368.00, 0.00, 0.00, 94122.00, 42246.00, 2, 1, 9, 10, 9, 10744.00, 134744.00, -92498.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:06'),
(496, 53, 42, 9, 42, 'Prudencio Botella Barranco', 51243.00, 51243.00, 0.00, 0.00, 24272.00, 26971.00, 2, 0, 0, 1, 1, 13521.00, 56521.00, -29550.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:06'),
(497, 53, 42, 9, 42, 'Adoración Sanmartín', 131555.00, 131555.00, 0.00, 0.00, 2386.00, 129169.00, 4, 7, 6, 3, 2, 7926.00, 195926.00, -66757.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:06'),
(498, 53, 41, 9, 41, 'María Jesús Huguet Giménez', 13319.00, 13319.00, 0.00, 0.00, 7780.00, 5539.00, 5, 2, 8, 8, 8, 3245.00, 187245.00, -181706.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:06'),
(499, 53, 42, 9, 42, 'Dulce Arnau', 148130.00, 148130.00, 0.00, 0.00, 14894.00, 133236.00, 4, 4, 9, 9, 8, 9979.00, 200979.00, -67743.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:06'),
(500, 54, 28, 6, 28, 'Rosario Pi Abad', 32964.00, 32964.00, 0.00, 0.00, 31101.00, 1863.00, 3, 9, 5, 10, 1, 2607.00, 198607.00, -196744.00, 'Registro de prueba generado automáticamente.', 5, '2025-11-24 20:51:06');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `maquina`
--

CREATE TABLE `maquina` (
  `id_maquina` int(11) NOT NULL,
  `id_sucursal` int(11) NOT NULL,
  `id_zona` int(11) NOT NULL,
  `numero_maquina` smallint(6) NOT NULL,
  `codigo_interno` varchar(80) DEFAULT NULL,
  `nombre_juego` varchar(120) DEFAULT NULL,
  `modelo` varchar(80) DEFAULT NULL,
  `numero_serie` varchar(120) DEFAULT NULL,
  `estado` enum('Operativa','Mantenimiento','Retirada') DEFAULT 'Operativa',
  `ubicacion_detalle` varchar(150) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `maquina`
--

INSERT INTO `maquina` (`id_maquina`, `id_sucursal`, `id_zona`, `numero_maquina`, `codigo_interno`, `nombre_juego`, `modelo`, `numero_serie`, `estado`, `ubicacion_detalle`, `created_at`) VALUES
(1, 1, 1, 1, 'INT-001', 'DRAGON', 'Modelo C', 'SN-430270', 'Operativa', 'Camino de Gonzalo Perea', '2025-11-24 20:51:02'),
(2, 1, 1, 2, 'INT-002', 'PIZZA', 'Modelo B', 'SN-852331', 'Operativa', 'Urbanización Artemio Fernandez', '2025-11-24 20:51:02'),
(3, 1, 1, 3, 'INT-003', 'PIZZA', 'Modelo A', 'SN-815174', 'Operativa', 'Pasadizo de Obdulia Corbacho', '2025-11-24 20:51:02'),
(4, 1, 1, 4, 'INT-004', 'EYE', 'Modelo A', 'SN-983628', 'Mantenimiento', 'Cuesta de Ruperto Valcárcel', '2025-11-24 20:51:02'),
(5, 1, 1, 5, 'INT-005', 'EYE', 'Modelo B', 'SN-270103', 'Operativa', 'Ronda Fidela Cano', '2025-11-24 20:51:02'),
(6, 1, 2, 6, 'INT-006', 'PIZZA', 'Modelo C', 'SN-515782', 'Operativa', 'Paseo Ángeles Figueroa', '2025-11-24 20:51:02'),
(7, 1, 2, 7, 'INT-007', 'DRAGON', 'Modelo C', 'SN-231797', 'Operativa', 'Ronda Cornelio Boada', '2025-11-24 20:51:02'),
(8, 1, 2, 8, 'INT-008', 'DRAGON', 'Modelo C', 'SN-998345', 'Mantenimiento', 'Paseo Tristán Benavides', '2025-11-24 20:51:03'),
(9, 1, 2, 9, 'INT-009', 'DRAGON', 'Modelo B', 'SN-994956', 'Operativa', 'Plaza Jimena Alberto', '2025-11-24 20:51:03'),
(10, 1, 2, 10, 'INT-010', 'DRAGON', 'Modelo A', 'SN-298826', 'Operativa', 'Vial de Ibán Lluch', '2025-11-24 20:51:03'),
(11, 1, 3, 11, 'INT-011', 'LION', 'Modelo B', 'SN-468870', 'Operativa', 'Glorieta de Leocadio Gomila', '2025-11-24 20:51:03'),
(12, 1, 3, 12, 'INT-012', 'DRAGON', 'Modelo B', 'SN-530167', 'Operativa', 'Cañada Elodia Cabañas', '2025-11-24 20:51:03'),
(13, 1, 3, 13, 'INT-013', 'FRUITS', 'Modelo A', 'SN-384391', 'Operativa', 'Pasaje Irene Vicente', '2025-11-24 20:51:03'),
(14, 1, 3, 14, 'INT-014', 'LION', 'Modelo A', 'SN-118757', 'Mantenimiento', 'Cañada Nazario Amigó', '2025-11-24 20:51:03'),
(15, 1, 3, 15, 'INT-015', 'DRAGON', 'Modelo C', 'SN-036394', 'Mantenimiento', 'Cañada Gaspar Calderón', '2025-11-24 20:51:03'),
(16, 2, 4, 16, 'INT-016', 'PIZZA', 'Modelo C', 'SN-719727', 'Operativa', 'Via de Gema Andreu', '2025-11-24 20:51:03'),
(17, 2, 4, 17, 'INT-017', 'LION', 'Modelo A', 'SN-879111', 'Mantenimiento', 'Acceso Duilio Jerez', '2025-11-24 20:51:03'),
(18, 2, 4, 18, 'INT-018', 'FRUITS', 'Modelo B', 'SN-761396', 'Operativa', 'Avenida Maricela Diego', '2025-11-24 20:51:03'),
(19, 2, 4, 19, 'INT-019', 'GOLD BAR', 'Modelo A', 'SN-775748', 'Mantenimiento', 'Urbanización Ramiro Ramis', '2025-11-24 20:51:03'),
(20, 2, 4, 20, 'INT-020', 'LION', 'Modelo B', 'SN-673092', 'Mantenimiento', 'Vial Graciela Carvajal', '2025-11-24 20:51:03'),
(21, 2, 5, 21, 'INT-021', 'LION', 'Modelo C', 'SN-412397', 'Mantenimiento', 'Paseo Guiomar Puerta', '2025-11-24 20:51:03'),
(22, 2, 5, 22, 'INT-022', 'PIZZA', 'Modelo B', 'SN-448409', 'Operativa', 'Via Pancho Salcedo', '2025-11-24 20:51:03'),
(23, 2, 5, 23, 'INT-023', 'DRAGON', 'Modelo C', 'SN-457900', 'Operativa', 'Calle de Gerardo Santos', '2025-11-24 20:51:03'),
(24, 2, 5, 24, 'INT-024', 'FRUITS', 'Modelo A', 'SN-152990', 'Operativa', 'Rambla de Isidro Llano', '2025-11-24 20:51:03'),
(25, 2, 5, 25, 'INT-025', 'DRAGON', 'Modelo A', 'SN-987675', 'Operativa', 'Acceso Norberto Montalbán', '2025-11-24 20:51:03'),
(26, 2, 6, 26, 'INT-026', 'GOLD BAR', 'Modelo A', 'SN-186584', 'Operativa', 'Pasaje de Concepción Torralba', '2025-11-24 20:51:03'),
(27, 2, 6, 27, 'INT-027', 'DRAGON', 'Modelo A', 'SN-575231', 'Mantenimiento', 'Ronda de María Fernanda Burgos', '2025-11-24 20:51:03'),
(28, 2, 6, 28, 'INT-028', 'EYE', 'Modelo B', 'SN-833645', 'Operativa', 'C. de Rosalva Carrera', '2025-11-24 20:51:03'),
(29, 2, 6, 29, 'INT-029', 'FRUITS', 'Modelo C', 'SN-711757', 'Operativa', 'Urbanización Eliseo Conde', '2025-11-24 20:51:03'),
(30, 2, 6, 30, 'INT-030', 'FRUITS', 'Modelo B', 'SN-160205', 'Mantenimiento', 'Callejón de Ildefonso Lopez', '2025-11-24 20:51:03'),
(31, 3, 7, 31, 'INT-031', 'GOLD BAR', 'Modelo C', 'SN-072921', 'Mantenimiento', 'Avenida de Ascensión Pellicer', '2025-11-24 20:51:03'),
(32, 3, 7, 32, 'INT-032', 'LION', 'Modelo B', 'SN-688866', 'Operativa', 'Urbanización de Domingo Abril', '2025-11-24 20:51:03'),
(33, 3, 7, 33, 'INT-033', 'GOLD BAR', 'Modelo B', 'SN-532441', 'Mantenimiento', 'Avenida de Gerardo Román', '2025-11-24 20:51:03'),
(34, 3, 7, 34, 'INT-034', 'LION', 'Modelo B', 'SN-787410', 'Operativa', 'Plaza de Lázaro Gargallo', '2025-11-24 20:51:03'),
(35, 3, 7, 35, 'INT-035', 'GOLD BAR', 'Modelo A', 'SN-687498', 'Operativa', 'Calle Carlota Grau', '2025-11-24 20:51:03'),
(36, 3, 8, 36, 'INT-036', 'PIZZA', 'Modelo C', 'SN-789301', 'Operativa', 'Via de Catalina Murcia', '2025-11-24 20:51:03'),
(37, 3, 8, 37, 'INT-037', 'GOLD BAR', 'Modelo B', 'SN-799969', 'Operativa', 'Vial de Soledad Ramirez', '2025-11-24 20:51:03'),
(38, 3, 8, 38, 'INT-038', 'EYE', 'Modelo B', 'SN-515009', 'Mantenimiento', 'Pasaje Oriana Llobet', '2025-11-24 20:51:03'),
(39, 3, 8, 39, 'INT-039', 'LION', 'Modelo B', 'SN-259799', 'Operativa', 'C. de Wilfredo Requena', '2025-11-24 20:51:03'),
(40, 3, 8, 40, 'INT-040', 'GOLD BAR', 'Modelo C', 'SN-421631', 'Mantenimiento', 'Ronda de Aránzazu Canet', '2025-11-24 20:51:03'),
(41, 3, 9, 41, 'INT-041', 'DRAGON', 'Modelo C', 'SN-262016', 'Operativa', 'Acceso de Esperanza Luján', '2025-11-24 20:51:03'),
(42, 3, 9, 42, 'INT-042', 'PIZZA', 'Modelo B', 'SN-300999', 'Operativa', 'Glorieta de Merche Ribes', '2025-11-24 20:51:03'),
(43, 3, 9, 43, 'INT-043', 'DRAGON', 'Modelo A', 'SN-580639', 'Mantenimiento', 'Avenida de Ambrosio Acevedo', '2025-11-24 20:51:03'),
(44, 3, 9, 44, 'INT-044', 'EYE', 'Modelo C', 'SN-737002', 'Operativa', 'Camino Juan José Bernat', '2025-11-24 20:51:03'),
(45, 3, 9, 45, 'INT-045', 'DRAGON', 'Modelo A', 'SN-727308', 'Operativa', 'Urbanización de Rosalva Casanovas', '2025-11-24 20:51:03');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sucursal`
--

CREATE TABLE `sucursal` (
  `id_sucursal` int(11) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  `telefono` varchar(50) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `sucursal`
--

INSERT INTO `sucursal` (`id_sucursal`, `nombre`, `direccion`, `telefono`, `created_at`) VALUES
(1, 'Local 1', 'Pasadizo Odalis Blanch 41\nTeruel, 46554', '+34716 60 17 61', '2025-11-24 20:51:02'),
(2, 'Local 2', 'Pasadizo Apolonia Cárdenas 90\nLa Rioja, 19262', '+34985 180 678', '2025-11-24 20:51:02'),
(3, 'Local 3', 'Urbanización de Emma Asenjo 3 Puerta 6 \nÁlava, 29949', '+34 841 48 75 16', '2025-11-24 20:51:02');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario`
--

CREATE TABLE `usuario` (
  `id_usuario` int(11) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `rol` enum('Atendedora','Encargado','Supervisor','Administrador') NOT NULL,
  `usuario_login` varchar(80) NOT NULL,
  `clave_hash` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`id_usuario`, `nombre`, `rol`, `usuario_login`, `clave_hash`, `created_at`) VALUES
(1, 'Administrador del sistema', 'Administrador', 'admin', 'HASH_ADMIN_DEMO', '2025-11-24 20:51:02'),
(2, 'Adriana de Moliner', 'Atendedora', 'user1', 'HASH_USER_DEMO', '2025-11-24 20:51:02'),
(3, 'Ester Vigil Cobo', 'Atendedora', 'user2', 'HASH_USER_DEMO', '2025-11-24 20:51:02'),
(4, 'Herberto Nacho Cuervo Calvet', 'Atendedora', 'user3', 'HASH_USER_DEMO', '2025-11-24 20:51:02'),
(5, 'Marina Francisca Romero Mármol', 'Atendedora', 'user4', 'HASH_USER_DEMO', '2025-11-24 20:51:02');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `zona`
--

CREATE TABLE `zona` (
  `id_zona` int(11) NOT NULL,
  `id_sursal` int(11) NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `orden` smallint(6) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `zona`
--

INSERT INTO `zona` (`id_zona`, `id_sursal`, `nombre`, `orden`, `created_at`) VALUES
(1, 1, 'Zona 1', 1, '2025-11-24 20:51:02'),
(2, 1, 'Zona 2', 2, '2025-11-24 20:51:02'),
(3, 1, 'Zona 3', 3, '2025-11-24 20:51:02'),
(4, 2, 'Zona 1', 1, '2025-11-24 20:51:02'),
(5, 2, 'Zona 2', 2, '2025-11-24 20:51:02'),
(6, 2, 'Zona 3', 3, '2025-11-24 20:51:02'),
(7, 3, 'Zona 1', 1, '2025-11-24 20:51:02'),
(8, 3, 'Zona 2', 2, '2025-11-24 20:51:02'),
(9, 3, 'Zona 3', 3, '2025-11-24 20:51:02');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `zona_lectura`
--

CREATE TABLE `zona_lectura` (
  `id_zonalect` int(11) NOT NULL,
  `id_cierre` int(11) NOT NULL,
  `id_zona` int(11) NOT NULL,
  `numero_maquina` smallint(6) NOT NULL,
  `nombre_juego` varchar(120) DEFAULT NULL,
  `entrada` decimal(14,2) DEFAULT NULL,
  `salida` decimal(14,2) DEFAULT NULL,
  `total` decimal(14,2) DEFAULT NULL,
  `orden` smallint(6) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `cierre_turno`
--
ALTER TABLE `cierre_turno`
  ADD PRIMARY KEY (`id_cierre`),
  ADD KEY `fk_cierre_sucursal` (`id_sucursal`),
  ADD KEY `fk_cierre_encargado` (`encargado_id`),
  ADD KEY `fk_cierre_createdby` (`created_by`);

--
-- Indices de la tabla `lectura_maquina`
--
ALTER TABLE `lectura_maquina`
  ADD PRIMARY KEY (`id_lectura`),
  ADD KEY `fk_lectura_cierre` (`id_cierre`),
  ADD KEY `fk_lectura_maquina` (`id_maquina`),
  ADD KEY `fk_lectura_zona` (`id_zona`),
  ADD KEY `fk_lectura_createdby` (`created_by`);

--
-- Indices de la tabla `maquina`
--
ALTER TABLE `maquina`
  ADD PRIMARY KEY (`id_maquina`),
  ADD KEY `fk_maquina_sucursal` (`id_sucursal`),
  ADD KEY `fk_maquina_zona` (`id_zona`);

--
-- Indices de la tabla `sucursal`
--
ALTER TABLE `sucursal`
  ADD PRIMARY KEY (`id_sucursal`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `uq_usuario_login` (`usuario_login`);

--
-- Indices de la tabla `zona`
--
ALTER TABLE `zona`
  ADD PRIMARY KEY (`id_zona`),
  ADD KEY `fk_zona_sucursal` (`id_sursal`);

--
-- Indices de la tabla `zona_lectura`
--
ALTER TABLE `zona_lectura`
  ADD PRIMARY KEY (`id_zonalect`),
  ADD KEY `fk_zonalect_cierre` (`id_cierre`),
  ADD KEY `fk_zonalect_zona` (`id_zona`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `cierre_turno`
--
ALTER TABLE `cierre_turno`
  MODIFY `id_cierre` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=55;

--
-- AUTO_INCREMENT de la tabla `lectura_maquina`
--
ALTER TABLE `lectura_maquina`
  MODIFY `id_lectura` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=501;

--
-- AUTO_INCREMENT de la tabla `maquina`
--
ALTER TABLE `maquina`
  MODIFY `id_maquina` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=46;

--
-- AUTO_INCREMENT de la tabla `sucursal`
--
ALTER TABLE `sucursal`
  MODIFY `id_sucursal` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `usuario`
--
ALTER TABLE `usuario`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `zona`
--
ALTER TABLE `zona`
  MODIFY `id_zona` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT de la tabla `zona_lectura`
--
ALTER TABLE `zona_lectura`
  MODIFY `id_zonalect` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `cierre_turno`
--
ALTER TABLE `cierre_turno`
  ADD CONSTRAINT `fk_cierre_createdby` FOREIGN KEY (`created_by`) REFERENCES `usuario` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_cierre_encargado` FOREIGN KEY (`encargado_id`) REFERENCES `usuario` (`id_usuario`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_cierre_sucursal` FOREIGN KEY (`id_sucursal`) REFERENCES `sucursal` (`id_sucursal`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `lectura_maquina`
--
ALTER TABLE `lectura_maquina`
  ADD CONSTRAINT `fk_lectura_cierre` FOREIGN KEY (`id_cierre`) REFERENCES `cierre_turno` (`id_cierre`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_lectura_createdby` FOREIGN KEY (`created_by`) REFERENCES `usuario` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_lectura_maquina` FOREIGN KEY (`id_maquina`) REFERENCES `maquina` (`id_maquina`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_lectura_zona` FOREIGN KEY (`id_zona`) REFERENCES `zona` (`id_zona`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `maquina`
--
ALTER TABLE `maquina`
  ADD CONSTRAINT `fk_maquina_sucursal` FOREIGN KEY (`id_sucursal`) REFERENCES `sucursal` (`id_sucursal`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_maquina_zona` FOREIGN KEY (`id_zona`) REFERENCES `zona` (`id_zona`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `zona`
--
ALTER TABLE `zona`
  ADD CONSTRAINT `fk_zona_sucursal` FOREIGN KEY (`id_sursal`) REFERENCES `sucursal` (`id_sucursal`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `zona_lectura`
--
ALTER TABLE `zona_lectura`
  ADD CONSTRAINT `fk_zonalect_cierre` FOREIGN KEY (`id_cierre`) REFERENCES `cierre_turno` (`id_cierre`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_zonalect_zona` FOREIGN KEY (`id_zona`) REFERENCES `zona` (`id_zona`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
