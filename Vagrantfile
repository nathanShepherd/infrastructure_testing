
# Network Infrastructure testing for pScheduler
# Developed by Nathan Shepherd for UofM:ITS

# -*- mode: ruby -*-
# # vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.define "server" do |server|

    server.vm.box = "geerlingguy/centos7"

    server.vm.network "private_network", ip: "172.28.128.3"

    server.vm.hostname = "server"

    server.vm.provision "shell", inline: <<-SHELL

       sudo curl -s -O https://raw.githubusercontent.com/perfsonar/pscheduler/master/scripts/system-prep

       sudo sh ./system-prep

       sudo yum install git

       git clone https://github.com/perfsonar/pscheduler.git --branch issue-155
       cd pscheduler
       sudo make

       sudo systemctl stop firewalld

    SHELL

  end

 

  config.vm.define "guest" do |guest|

      guest.vm.box = "geerlingguy/centos7"

      guest.vm.network "private_network", ip: "172.28.128.4"

      guest.vm.hostname = "guest"

      guest.vm.provision "shell", inline: <<-SHELL

        sudo curl -s -O https://raw.githubusercontent.com/perfsonar/pscheduler/master/scripts/system-prep

        sudo sh ./system-prep

        sudo yum install git

        git clone https://github.com/perfsonar/pscheduler.git --branch issue-155
        cd pscheduler
        sudo make

        sudo systemctl stop firewalld

    SHELL

  end

end
