(function () {
    'use strict';

    angular.module('PerekrestorOrderStats', [])
        .controller('MainController', MainController)


    MainController.$inject = ['$http']
    function MainController($http) {
        let ctrl = this;
        ctrl.startDate = computeDefaultStartDate();
        ctrl.endDate = new Date();
        ctrl.showDetails = false;
        ctrl.showFilters = false;
        ctrl.exportedData = [];
        ctrl.filteredData = [];
        ctrl.statsData = {};
        ctrl.sortedData = [];

        ctrl.launch = function () {
            ctrl.showFilters = true;
            ctrl.showDetails = false;
            ctrl.filteredData = [];
            ctrl.statsData = {};
            ctrl.topAmountProduct = {'totalAmount': 0};
            ctrl.topCostProduct = {'totalCost': 0};
            filterData();
            calculateStats();
            findTop();
        }

        ctrl.sortByPrice = function () {
            ctrl.showDetails = true;
            ctrl.sortedData = [];
            if (Object.keys(ctrl.statsData).length == 0) {
                ctrl.launch();
            }
            for (let productID in ctrl.statsData) {
                let i = 0;
                console.log(ctrl.statsData[productID]);
                for (i in ctrl.sortedData)
                {
                    console.log(i);
                    if (ctrl.statsData[productID]['avgPrice'] > ctrl.sortedData[i]['avgPrice']) {
                        break;
                    }
                }
                ctrl.sortedData.splice(i,0,ctrl.statsData[productID]);
            }
        }

        ctrl.sortByCost = function () {
            ctrl.showDetails = true;
            ctrl.sortedData = [];
            if (Object.keys(ctrl.statsData).length == 0) {
                ctrl.launch();
            }
            for (let productID in ctrl.statsData) {
                let i = 0;
                console.log(ctrl.statsData[productID]);
                for (i in ctrl.sortedData)
                {
                    console.log(i);
                    if (ctrl.statsData[productID]['totalCost'] > ctrl.sortedData[i]['totalCost']) {
                        break;
                    }
                }
                ctrl.sortedData.splice(i,0,ctrl.statsData[productID]);
            }
        }

        ctrl.sortByAmount = function () {
            ctrl.showDetails = true;
            ctrl.sortedData = [];
            if (Object.keys(ctrl.statsData).length == 0) {
                ctrl.launch();
            }
            for (let productID in ctrl.statsData) {
                let i = 0;
                console.log(ctrl.statsData[productID]);
                for (i in ctrl.sortedData)
                {
                    console.log(i);
                    if (ctrl.statsData[productID]['totalAmount'] > ctrl.sortedData[i]['totalAmount']) {
                        break;
                    }
                }
                ctrl.sortedData.splice(i,0,ctrl.statsData[productID]);
            }
        }

        function computeDefaultStartDate() {
            let currentDate = new Date();
            return new Date(currentDate.getFullYear() - 1, 0, 1);
        }

        function filterData() {
            for (let i in ctrl.exportedData) {
                let productDate1 = ctrl.exportedData[i]['date'].split('.');
                let productDate = new Date(productDate1[2], parseInt(productDate1[1]) - 1, productDate1[0]);
                if (productDate >= ctrl.startDate && productDate <= ctrl.endDate) {
                    ctrl.filteredData.push(ctrl.exportedData[i]);
                }
            }
        }

        function calculateStats() {
            for (let i in ctrl.filteredData) {
                let productID = ctrl.filteredData[i]['id'];
                if (!(productID in ctrl.statsData)) {
                    ctrl.statsData[productID] = {'totalAmount': 0, 'totalCost': 0};
                    ctrl.statsData[productID]['amount_unit'] = ctrl.filteredData[i]['amount_unit'];
                    ctrl.statsData[productID]['title'] = ctrl.filteredData[i]['title'];
                    ctrl.statsData[productID]['link'] = ctrl.filteredData[i]['link'];
                    ctrl.statsData[productID]['img'] = ctrl.filteredData[i]['img'];
                    ctrl.statsData[productID]['category'] = ctrl.filteredData[i]['category'];
                    ctrl.statsData[productID]['id'] = productID;
                }
                ctrl.statsData[productID]['totalAmount'] += parseFloat(ctrl.filteredData[i]['amount']);
                ctrl.statsData[productID]['totalCost'] += (parseFloat(ctrl.filteredData[i]['price']) * parseFloat(ctrl.filteredData[i]['amount']));
            }
        }

        function findTop() {
            for (let productID in ctrl.statsData) {
                ctrl.statsData[productID]['avgPrice'] = ctrl.statsData[productID]['totalCost'] / ctrl.statsData[productID]['totalAmount'];
                if (ctrl.statsData[productID]['totalAmount'] > ctrl.topAmountProduct['totalAmount']) {
                    ctrl.topAmountProduct = ctrl.statsData[productID];
                }
                if (ctrl.statsData[productID]['totalCost'] > ctrl.topCostProduct['totalCost']) {
                    ctrl.topCostProduct = ctrl.statsData[productID];
                }
            }
        }
    }


})();